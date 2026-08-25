import { toRaw } from 'vue'

/**
 * Standardized deep cloning utility that safely unwraps reactive UI proxies
 * (Vue 3 proxies) and recursively duplicates nested data structures, preserving
 * complex data types (Date, RegExp, Map, Set, ArrayBuffer, TypedArrays, etc.)
 * without falling back to JSON serialization.
 *
 * @param {any} value - The object or value to clone.
 * @param {WeakMap} [seen=new WeakMap()] - Map for handling circular references.
 * @returns {any} A deep copy of the value.
 */
export function deepClone(value, seen = new WeakMap()) {
  if (value === null || typeof value !== 'object') {
    return value
  }

  // Unwrap Vue reactive proxy if present
  const raw = toRaw(value)

  if (raw === null || typeof raw !== 'object') {
    return raw
  }

  // Prevent circular references
  if (seen.has(raw)) {
    return seen.get(raw)
  }

  // Preserve Date
  if (raw instanceof Date) {
    return new Date(raw.getTime())
  }

  // Preserve RegExp
  if (raw instanceof RegExp) {
    return new RegExp(raw.source, raw.flags)
  }

  // Preserve Map
  if (raw instanceof Map) {
    const copy = new Map()
    seen.set(raw, copy)
    for (const [k, v] of raw.entries()) {
      copy.set(deepClone(k, seen), deepClone(v, seen))
    }
    return copy
  }

  // Preserve Set
  if (raw instanceof Set) {
    const copy = new Set()
    seen.set(raw, copy)
    for (const v of raw.values()) {
      copy.add(deepClone(v, seen))
    }
    return copy
  }

  // Preserve ArrayBuffer
  if (raw instanceof ArrayBuffer) {
    return raw.slice(0)
  }

  // Preserve TypedArrays (Uint8Array, Float32Array, etc.)
  if (ArrayBuffer.isView(raw) && !(raw instanceof DataView)) {
    return new raw.constructor(raw)
  }

  // Preserve Array
  if (Array.isArray(raw)) {
    const copy = new Array(raw.length)
    seen.set(raw, copy)
    for (let i = 0; i < raw.length; i++) {
      copy[i] = deepClone(raw[i], seen)
    }
    return copy
  }

  // Plain objects and custom object instances
  const copy = Object.create(Object.getPrototypeOf(raw))
  seen.set(raw, copy)

  for (const key of Reflect.ownKeys(raw)) {
    const desc = Object.getOwnPropertyDescriptor(raw, key)
    if (desc && desc.enumerable) {
      copy[key] = deepClone(raw[key], seen)
    }
  }

  return copy
}

export default deepClone
