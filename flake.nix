{
  description = "CartiChrono";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-25.05";

  outputs =
    { self, nixpkgs }:
    let
      pkgs = import nixpkgs {
        system = "x86_64-linux";
      };
      pythonPackages = pkgs.python313Packages;
      pyPkgs = with pythonPackages; [
        python-dotenv
        pip
        nextcord
        pynacl
        cffi
        pyogg
        opuslib
        gtts
        pynacl

      ];
    in
    {
      devShells.x86_64-linux = {
        default = pkgs.mkShell {
          buildInputs = [
            pyPkgs
            pkgs.ffmpeg
            pkgs.libopus
            pkgs.libsodium
            pkgs.pkg-config
            pkgs.alsa-lib
            pkgs.pulseaudio
            pkgs.pavucontrol
          ];

          shellHook = ''
            export PULSE_RUNTIME_PATH=/run/user/$(id -u)/pulse
            export XDG_RUNTIME_DIR=/run/user/$(id -u)
          '';
        };
      };
    };
}
