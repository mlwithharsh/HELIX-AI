package com.helix.ai;

import android.content.res.AssetManager;
import android.util.Log;

public class LlamaModel {
    private static final String TAG = "Helix.Llama";
    private long context = 0;

    static {
        System.loadLibrary("llama"); // libllama.so
        System.loadLibrary("native-lib"); // Our JNI bridge
    }

    public native long loadModel(AssetManager assetManager, String modelPath);
    public native void unloadModel(long context);
    public native String generateText(long context, String prompt, int maxTokens);

    public boolean isLoaded() {
        return context != 0;
    }

    public void load(AssetManager assets, String path) {
        context = loadModel(assets, path);
        if (context != 0) {
            Log.i(TAG, "Edge AI Model Loaded Successfully");
        } else {
            Log.e(TAG, "Failed to load Edge AI Model");
        }
    }

    public String chat(String prompt) {
        if (context == 0) return "Edge AI not ready.";
        return generateText(context, prompt, 512);
    }
}
