#include <simde/wasm/simd128.h>

v128_t
u32x4_gt(v128_t a, v128_t b) {
  return wasm_u32x4_gt(a, b);
}
