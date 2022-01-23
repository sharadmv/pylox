{ stdenv, llvm-project, cmake, ninja, clang, python39, lld, zlib, git }:
stdenv.mkDerivation {
  name = "mlir";
  src = "${llvm-project}";
  nativeBuildInputs = [
    cmake
    ninja
    clang
    python39
    lld
  ];
  propagatedBuildInputs = [
    zlib
    git
  ];
  postUnpack = ''
    sourceRoot=source/llvm
  '';
  preBuild = ''
    mkdir -p $out/
    ln -sv $PWD/lib $out
  '';
  cmakeFlags = [
    "-DLLVM_ENABLE_PROJECTS=mlir"
    "-DLLVM_BUILD_EXAMPLES=ON"
    "-DLLVM_TARGETS_TO_BUILD='X86;NVPTX;AMDGPU'"
    "-DCMAKE_BUILD_TYPE=Release"
    "-DLLVM_ENABLE_ASSERTIONS=ON"
    "-DCMAKE_C_COMPILER=clang"
    "-DCMAKE_CXX_COMPILER=clang++"
    "-DLLVM_ENABLE_LLD="
  ];
  doCheck = false;
  enableParallelBuilding = true;
}
