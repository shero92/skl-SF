# Lighting FX implementation

Hero Room includes three reusable `RoomLightFX` instances in its JSON `effects` list.

Each effect pulls **individual transparent PNGs** from the catalog:
- `D012`, `D013`, `D014`: animated flame sequence (separate files).
- `D015`: wide lantern glow.
- `D016`: narrower candle glow.

The effect reads `kind`, `x`, `y`, `scale` and `glow_alpha` from room JSON. It animates the flames and softly pulses the light opacity. Layers are drawn in `AnimatedLighting`; no new texture is baked into existing walls, lamps or furniture.

These effects are first-pass originals and need visual review against the global lighting direction of the artwork.
