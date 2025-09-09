{
  description = "GStrummer - Guitar strumming trainer (PySide6, sounddevice, librosa)";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {inherit system;};

      python = pkgs.python312;

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
          pyfluidsynth
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
          ${pkgs.lib.optionalString pkgs.stdenv.isLinux ''
            # Prefer Wayland if available; fallback to XCB
            export QT_QPA_PLATFORM=wayland,xcb
          ''}
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
        buildInputs =
          [
            pythonEnv
            # System libs for runtime
            pkgs.portaudio
            pkgs.libsndfile
            # Full Qt stack for PySide6 (plugins, platform backends)
            pkgs.qt6.full
            pkgs.pkg-config
            pkgs.git
          ]
          ++ pkgs.lib.optionals pkgs.stdenv.isLinux [
            # Wayland platform plugin on Linux (optional but recommended)
            pkgs.qt6.qtwayland
          ];

        shellHook = ''
          echo "🔧 GStrummer dev shell activated"
          echo " - Run GUI:     nix run"
          echo " - Run console: nix run .#console"
          echo " - Python:      $(python --version)"
          # Make sure local sources are importable if needed
          export PYTHONPATH="$PWD:$PYTHONPATH"
          # Reduce glitches in some Pulse setups
          ${pkgs.lib.optionalString pkgs.stdenv.isLinux "export PULSE_LATENCY_MSEC=30"}
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
