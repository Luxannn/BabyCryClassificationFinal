import tensorflow as tf

# Load the model in unsafe mode
model = tf.keras.models.load_model(
    "BabyCry_CRNN_Attention_Final.keras",
    compile=False,
    safe_mode=False,
    custom_objects={"tf": tf, "<lambda>": lambda x: x}
)

# Manually define the missing output shape for Lambda layers
for layer in model.layers:
    if isinstance(layer, tf.keras.layers.Lambda):
        layer._output_shape = (None, 256)

# Save a new “clean” version without problematic Lambda metadata
model.save("BabyCry_CRNN_Attention_Fixed.keras")
print("✅ Fixed model saved as BabyCry_CRNN_Attention_Fixed.keras")
