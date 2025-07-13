{
  description = "flake with FHS environment for Pixi";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    { nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
        fhs = pkgs.buildFHSEnv {
          name = "jellyfin-library-helper";
          targetPkgs =
            ps: with ps; [
              pixi
            ];
          # multiPkgs = ps: with ps; [ ]; # 32-bit libs
          runScript = "bash";
        };
      in
      {
        devShells.default = fhs.env;
      }
    );
}
