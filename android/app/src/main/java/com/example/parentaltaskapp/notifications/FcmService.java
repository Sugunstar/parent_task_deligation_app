package com.example.parentaltaskapp.notifications;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.core.app.NotificationCompat;

import com.example.parentaltaskapp.ui.approval.ApprovalCardActivity;
import com.example.parentaltaskapp.ui.emergency.EmergencyAlertActivity;
import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

public class FcmService extends FirebaseMessagingService {

    private static final String TAG = "FcmService";
    private static final String CHANNEL_ID = "parental_task_channel";
    private static final String EMERGENCY_CHANNEL_ID = "emergency_channel";

    @Override
    public void onMessageReceived(@NonNull RemoteMessage message) {
        super.onMessageReceived(message);
        
        Log.d(TAG, "Message received from: " + message.getFrom());

        if (message.getData().size() > 0) {
            String type = message.getData().get("type");
            if ("emergency".equals(type)) {
                showEmergencyNotification(message.getData().get("summary"));
            } else {
                showApprovalNotification(message.getData().get("summary"));
            }
        }
    }

    private void showApprovalNotification(String summary) {
        createNotificationChannels();

        Intent intent = new Intent(this, ApprovalCardActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent pendingIntent = PendingIntent.getActivity(this, 0, intent,
                PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_ONE_SHOT);

        NotificationCompat.Builder builder = new NotificationCompat.Builder(this, CHANNEL_ID)
                .setSmallIcon(android.R.drawable.ic_dialog_info)
                .setContentTitle("New Task Approval")
                .setContentText(summary)
                .setAutoCancel(true)
                .setContentIntent(pendingIntent);

        NotificationManager manager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        manager.notify(1, builder.build());
    }

    private void showEmergencyNotification(String summary) {
        createNotificationChannels();

        Intent intent = new Intent(this, EmergencyAlertActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        PendingIntent pendingIntent = PendingIntent.getActivity(this, 0, intent,
                PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);

        NotificationCompat.Builder builder = new NotificationCompat.Builder(this, EMERGENCY_CHANNEL_ID)
                .setSmallIcon(android.R.drawable.ic_dialog_alert)
                .setContentTitle("EMERGENCY DETECTED")
                .setContentText(summary)
                .setPriority(NotificationCompat.PRIORITY_MAX)
                .setCategory(NotificationCompat.CATEGORY_ALARM)
                .setFullScreenIntent(pendingIntent, true)
                .setAutoCancel(false)
                .setOngoing(true);

        NotificationManager manager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        manager.notify(2, builder.build());
    }

    private void createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManager manager = getSystemService(NotificationManager.class);
            
            // Standard Channel
            NotificationChannel channel = new NotificationChannel(
                    CHANNEL_ID, "Task Approvals", NotificationManager.IMPORTANCE_HIGH);
            manager.createNotificationChannel(channel);

            // Emergency Channel
            NotificationChannel emergencyChannel = new NotificationChannel(
                    EMERGENCY_CHANNEL_ID, "Emergency Alerts", NotificationManager.IMPORTANCE_MAX);
            // In a real app, set custom sound, vibration, bypass DND, etc.
            manager.createNotificationChannel(emergencyChannel);
        }
    }

    @Override
    public void onNewToken(@NonNull String token) {
        Log.d(TAG, "Refreshed token: " + token);
        // Send token to backend
    }
}
