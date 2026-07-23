package com.example.parentaltaskapp.call;

import android.content.Context;
import android.net.Uri;
import android.util.Log;

import com.example.parentaltaskapp.network.ApiService;
import com.example.parentaltaskapp.network.RetrofitClient;

import java.io.File;

import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ManualUploadAudioSource {

    private static final String TAG = "ManualUploadAudioSource";
    private final ApiService apiService;

    public ManualUploadAudioSource() {
        this.apiService = RetrofitClient.getService();
    }

    public void uploadAudioFile(Context context, Uri fileUri, String childId, String timestamp) {
        // In a real app, you would resolve the URI to a real File path or read bytes directly
        File file = new File(fileUri.getPath()); // Simplified for prototype
        
        RequestBody requestFile = RequestBody.create(MediaType.parse("audio/*"), file);
        MultipartBody.Part body = MultipartBody.Part.createFormData("audio_file", file.getName(), requestFile);

        RequestBody childIdBody = RequestBody.create(MediaType.parse("text/plain"), childId);
        RequestBody timestampBody = RequestBody.create(MediaType.parse("text/plain"), timestamp);

        Call<ResponseBody> call = apiService.uploadAudio(body, childIdBody, timestampBody);
        call.enqueue(new Callback<ResponseBody>() {
            @Override
            public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
                if (response.isSuccessful()) {
                    Log.d(TAG, "Upload successful");
                    // Proceed to process the call...
                } else {
                    Log.e(TAG, "Upload failed: " + response.code());
                }
            }

            @Override
            public void onFailure(Call<ResponseBody> call, Throwable t) {
                Log.e(TAG, "Upload error: ", t);
            }
        });
    }
}
