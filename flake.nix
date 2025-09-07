{
  description = "GStrummer - Guitar strumming trainer (PySide6, sounddevice, librosa)";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {inherit system;};

      python = pkgs.python311;

      pythonEnv = python.withPackages (ps:
        with ps; [
          # GUI
          pyside6

          # Audio / DSP stack
          numpy
          scipy
          numba
          sounddevice
          soundfile # pysoundfile (libsndfile backend)
          audioread
          librosa
          pyyaml

          # Dev tooling
          pytest
          mypy
          black
          ruff
          pyinstaller
        ]);

      # Shell app to run GUI from the source tree
      gstrummer = pkgs.writeShellApplication {
        name = "gstrummer";
        runtimeInputs = [pythonEnv];
        text = ''
          cd ${./.}
          # Prefer Wayland if доступно; откат на XCB
          export QT_QPA_PLATFORM=${pkgs.lib.mkIf (pkgs.stdenv.isLinux) "wayland,xcb"}
          exec python app/main.py "$@"
        '';
      };

      # Shell app to run console version
      gstrummer-console = pkgs.writeShellApplication {
        name = "gstrummer-console";
        runtimeInputs = [pythonEnv];
        text = ''
          cd ${./.}
          exec python guitar_trainer.py "$@"
        '';
      };
    in {
      # nix develop
      devShells.default = pkgs.mkShell {
        buildInputs = [
          pythonEnv
          # System libs for runtime
          pkgs.portaudio
          pkgs.libsndfile
          # Full Qt stack for PySide6 (plugins, platform backends)
          pkgs.qt6.full
          # Wayland platform plugin on Linux (optional but recommended)
          pkgs.qt6.qtwayland
          pkgs.pkg-config
          pkgs.git
        ];

        shellHook = ''
          echo "🔧 GStrummer dev shell activated"
          echo " - Run GUI:     nix run"
          echo " - Run console: nix run .#console"
          echo " - Python:      $(python --version)"
          # Make sure local sources are importable if needed
          export PYTHONPATH="$PWD:$PYTHONPATH"
          # Reduce glitches in some Pulse setups
          export PULSE_LATENCY_MSEC=30
        '';
      };

      # nix run (GUI)
      apps.default = {
        type = "app";
        program = "${gstrummer}/bin/gstrummer";
      };

      # nix run .#console (TUI)
      apps.console = {
        type = "app";
        program = "${gstrummer-console}/bin/gstrummer-console";
      };

      # Optional: expose the wrappers as packages
      packages.default = gstrummer;
      packages.console = gstrummer-console;
    });
}
