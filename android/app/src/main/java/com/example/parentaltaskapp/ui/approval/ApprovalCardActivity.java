package com.example.parentaltaskapp.ui.approval;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.parentaltaskapp.network.ApiService;
import com.example.parentaltaskapp.network.RetrofitClient;

import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ApprovalCardActivity extends AppCompatActivity {

    private int currentTaskId = 1; // Example ID
    private ApiService apiService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // setContentView(R.layout.activity_approval_card);
        
        apiService = RetrofitClient.getService();
        
        // Mocking UI elements
        // TextView summaryText = findViewById(R.id.summaryText);
        // Button acceptBtn = findViewById(R.id.acceptButton);
        // Button declineBtn = findViewById(R.id.declineButton);
        
        // summaryText.setText("Order pizza from Domino's");
        
        /*
        acceptBtn.setOnClickListener(v -> submitDecision("approved"));
        declineBtn.setOnClickListener(v -> submitDecision("declined"));
        */
    }

    private void submitDecision(String decision) {
        ApiService.DecisionRequest request = new ApiService.DecisionRequest(decision);
        
        apiService.submitDecision(currentTaskId, request).enqueue(new Callback<ResponseBody>() {
            @Override
            public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
                if (response.isSuccessful()) {
                    Toast.makeText(ApprovalCardActivity.this, "Decision submitted", Toast.LENGTH_SHORT).show();
                    finish();
                }
            }

            @Override
            public void onFailure(Call<ResponseBody> call, Throwable t) {
                Toast.makeText(ApprovalCardActivity.this, "Error submitting decision", Toast.LENGTH_SHORT).show();
            }
        });
    }
}
