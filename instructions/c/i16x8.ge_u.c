#include <wasm_simd128.h>

v128_t
i16x8_ge_u(v128_t a, v128_t b)
{
  return wasm_u16x8_ge(a, b);
}