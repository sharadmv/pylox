{
  description = "Pylox";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    llvm-project = {
      url = "github:llvm/llvm-project";
      flake = false;
    };
    poetry2nix.url = "github:nix-community/poetry2nix";
  };

  outputs = { self, nixpkgs, flake-utils, llvm-project, poetry2nix }:
  {
    overlay = nixpkgs.lib.composeManyExtensions [
      poetry2nix.overlay
      (final: prev: {
        pylox = prev.poetry2nix.mkPoetryApplication {
          python = prev.python310;
          projectDir = ./.;
        };
        pylox-env = prev.poetry2nix.mkPoetryEnv {
          editablePackageSources = {
            pylox = ./pylox;
          };
          python = prev.python310;
          projectDir = ./.;
        };
      })
    ];
  } // flake-utils.lib.eachDefaultSystem (system:
  let
    pkgs = import nixpkgs {
      inherit system;
      overlays = [ self.overlay ];
    };
  in
  rec {
    packages = {
      pylox = pkgs.pylox;
    };

    defaultPackage = packages.pylox;

    devShell = pkgs.mkShell {
      buildInputs = with pkgs; [
        poetry
        python310
        pylox-env
      ];
    };
  });
}
