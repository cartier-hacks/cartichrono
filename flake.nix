{
  description = "CartiChrono Discord bot";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-25.05";

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      py = pkgs.python313;
    in
    {
      devShells.x86_64-linux.default = pkgs.mkShell {
        packages = [
          pkgs.python313
          pkgs.ffmpeg
          pkgs.libopus
          pkgs.libsodium
          pkgs.pkg-config
          pkgs.cacert
          pkgs.openssl
          pkgs.gnumake
        ];

        shellHook = ''
          export SSL_CERT_FILE=${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt
          export REQUESTS_CA_BUNDLE=${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt
          export LD_LIBRARY_PATH=${pkgs.libopus}/lib:${pkgs.libsodium}/lib:$LD_LIBRARY_PATH
          export PULSE_RUNTIME_PATH=/run/user/$(id -u)/pulse
          export XDG_RUNTIME_DIR=/run/user/$(id -u)
          source venv/bin/activate
        '';
      };

    };
}
