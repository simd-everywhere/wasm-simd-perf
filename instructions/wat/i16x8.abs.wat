(module
  (type (;0;) (func (param v128) (result v128)))
  (func $i16x8_abs (type 0) (param v128) (result v128)
    local.get 0
    i16x8.abs)
  (memory (;0;) 2)
  (global $__stack_pointer (mut i32) (i32.const 66560))
  (export "memory" (memory 0))
  (export "i16x8_abs" (func $i16x8_abs)))