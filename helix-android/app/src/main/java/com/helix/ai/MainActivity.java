package com.helix.ai;

import android.content.Context;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

public class MainActivity extends AppCompatActivity {
    private static final String TAG = "Helix.Main";
    private static final String BACKEND_URL = "https://reworked-echo.onrender.com/api/chat";

    private EditText inputEdit;
    private TextView chatText;
    private Button sendButton;
    private ScrollView chatScroll;
    private LlamaModel edgeModel;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        inputEdit = findViewById(R.id.chat_input);
        chatText = findViewById(R.id.chat_text);
        sendButton = findViewById(R.id.send_button);
        chatScroll = findViewById(R.id.chat_scroll);

        edgeModel = new LlamaModel();
        
        // Initialize Edge AI in background
        new Thread(() -> {
            edgeModel.load(getAssets(), "models/helix-q4_k_m.gguf");
        }).start();

        sendButton.setOnClickListener(v -> {
            String userInput = inputEdit.getText().toString().trim();
            if (userInput.isEmpty()) return;
            
            appendChat("User", userInput);
            inputEdit.setText("");
            
            if (isOnline()) {
                callCloudAPI(userInput);
            } else {
                callLocalEdge(userInput);
            }
        });
    }

    private boolean isOnline() {
        ConnectivityManager cm = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo info = cm.getActiveNetworkInfo();
        return info != null && info.isConnected();
    }

    private void appendChat(String sender, String text) {
        runOnUiThread(() -> {
            chatText.append(sender + ": " + text + "\n\n");
            chatScroll.fullScroll(View.FOCUS_DOWN);
        });
    }

    private void callCloudAPI(String prompt) {
        new Thread(() -> {
            try {
                URL url = new URL(BACKEND_URL);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setRequestProperty("Content-Type", "application/json");
                conn.setDoOutput(true);

                String json = "{\"message\":\"" + prompt + "\", \"mode\":\"cloud\"}";
                try (OutputStream os = conn.getOutputStream()) {
                    os.write(json.getBytes());
                }

                if (conn.getResponseCode() == 200) {
                    BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                    StringBuilder res = new StringBuilder();
                    String line;
                    while ((line = in.readLine()) != null) res.append(line);
                    
                    // Simple parse for demo (Interaction payload)
                    appendChat("Cloud AI", res.toString());
                } else {
                    // Fallback to Edge on Cloud failure
                    Log.w(TAG, "Cloud API Failed. Falling back to Edge.");
                    callLocalEdge(prompt);
                }
            } catch (Exception e) {
                Log.e(TAG, "Cloud Error: " + e.getMessage());
                callLocalEdge(prompt);
            }
        }).start();
    }

    private void callLocalEdge(String prompt) {
        appendChat("Edge AI", "... (processing offline)");
        new Thread(() -> {
            String res = edgeModel.chat(prompt);
            appendChat("Edge AI", res);
        }).start();
    }
}
