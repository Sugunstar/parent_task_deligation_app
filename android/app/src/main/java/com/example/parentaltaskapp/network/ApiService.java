package com.example.parentaltaskapp.network;

import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.GET;
import retrofit2.http.Multipart;
import retrofit2.http.POST;
import retrofit2.http.Part;
import retrofit2.http.Path;

public interface ApiService {

    @Multipart
    @POST("calls/upload")
    Call<ResponseBody> uploadAudio(
            @Part MultipartBody.Part audioFile,
            @Part("child_id") RequestBody childId,
            @Part("call_timestamp") RequestBody timestamp
    );

    @POST("calls/{call_id}/process")
    Call<ResponseBody> processCall(@Path("call_id") String callId);

    @POST("tasks/{task_id}/decision")
    Call<ResponseBody> submitDecision(@Path("task_id") int taskId, @Body DecisionRequest decision);

    class DecisionRequest {
        public String decision;
        public DecisionRequest(String decision) { this.decision = decision; }
    }
}
