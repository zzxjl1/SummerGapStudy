package com.idealbroker.aisee;

import static com.idealbroker.aisee.MainActivity.refreshMicServiceState;

import android.Manifest;
import android.app.Service;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.os.IBinder;
import android.util.Log;
import android.view.View;

import androidx.annotation.Nullable;
import androidx.core.app.ActivityCompat;

import com.hjq.permissions.OnPermissionCallback;
import com.hjq.permissions.Permission;
import com.hjq.permissions.XXPermissions;
import com.kongzue.dialogx.dialogs.MessageDialog;
import com.kongzue.dialogx.dialogs.PopTip;
import com.kongzue.dialogx.interfaces.OnDialogButtonClickListener;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.drafts.Draft_6455;
import org.java_websocket.extensions.permessage_deflate.PerMessageDeflateExtension;
import org.java_websocket.handshake.ServerHandshake;
import org.json.JSONException;
import org.json.JSONObject;
import com.idealbroker.aisee.STTCallback;
import java.net.URI;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

public class MicService extends Service {
    private final static int AUDIO_SOURCE = MediaRecorder.AudioSource.VOICE_RECOGNITION;
    private final static int SAMPLE_RATE = 8000;
    private final static int CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO;
    private final static int AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT;
    private static final String TAG = "AudioEncoder";
    public static boolean running = false;
    private static int mBufferSizeInBytes = 1024 * 5 * 2;
    private static AudioRecord mAudioRecord;
    private static Executor mExecutor = Executors.newSingleThreadExecutor();
    private static WebSocketClient ws;
    private static STTCallback callback = new STTCallback() ;

    public static void setCallback(STTCallback callback) {
        MicService.callback = callback;
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Log.e(TAG, "onStartCommand");
        if (!XXPermissions.isGranted(MyApplication.context, Permission.RECORD_AUDIO)) {
            MyApplication.tts.speek("???????????????????????????????????????????????????????????????????????????????????????", true, true);
            XXPermissions.with(MainActivity.base)
                    .permission(Permission.RECORD_AUDIO)
                    .request(new OnPermissionCallback() {

                        @Override
                        public void onGranted(List<String> permissions, boolean all) {
                            start();
                        }

                        @Override
                        public void onDenied(List<String> permissions, boolean never) {
                            ToolUtils.showToastMessage(MyApplication.context, "??????????????????", 2000);
                            MyApplication.tts.speek("??????????????????????????????????????????", true, true);
                            stopSelf();
                        }
                    });
        } else {
            start();
        }
        return super.onStartCommand(intent, flags, startId);
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        stop();
    }

    public static boolean isRunning() {
        return running;
    }

    public static void start() {

        if (ActivityCompat.checkSelfPermission(MyApplication.context, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            Log.e(TAG, "?????????????????????");
            return;
        }
        mAudioRecord = new AudioRecord(AUDIO_SOURCE, SAMPLE_RATE, CHANNEL_CONFIG, AUDIO_FORMAT, mBufferSizeInBytes);
        create_ws_conn();
    }

    public static void stop() {
        running = false;
        MyApplication.tts.speek("??????????????????", true, true);
        if (mAudioRecord != null) {
            mAudioRecord.stop();
            mAudioRecord.release();
        }
        if (ws != null) ws.close();
        refreshMicServiceState();
    }

    private static void create_ws_conn() {
        Log.e(TAG, "WS CONNECTING");
        String url = MyApplication.settings.getString("ws_base_url", MyApplication.context.getResources().getString(R.string.ws_base_url_default)) + "/stt";
        ws = new WebSocketClient(URI.create(url), new Draft_6455(new PerMessageDeflateExtension())) {

            @Override
            public void onMessage(String message) {
                Log.e(TAG, message);
                try {
                    JSONObject t = new JSONObject(message);
                    String text = t.getString("text");
                    int type= t.getInt("type");
                    switch (type){
                        case 0:
                            callback.onProcedure(text);
                            break;
                        case 1:
                            callback.onEnd(text);
                            break;
                    }
                } catch (JSONException e) {
                    e.printStackTrace();
                }

            }

            @Override
            public void onOpen(ServerHandshake handshake) {
                Log.e(TAG, "????????????");
                mExecutor.execute(new Runnable() {
                    @Override
                    public void run() {

                        if (mAudioRecord.getState() != AudioRecord.STATE_INITIALIZED) return;
                        mAudioRecord.startRecording();

                        running = true;
                        MyApplication.tts.speek("??????????????????", true, true);
                        PopTip.show(R.mipmap.ai_apeech, "????????????????????????????????????").setAutoTintIconInLightOrDarkMode(false);
                        refreshMicServiceState();
                        byte[] buffer = new byte[mBufferSizeInBytes];
                        Log.e(TAG, "??????????????????");
                        while (running) {
                            mAudioRecord.read(buffer, 0, mBufferSizeInBytes);

                            short[] t = new short[buffer.length / 2];
                            for (int i = 0; i < buffer.length; i += 2) {
                                short value = (short) (((buffer[i + 1] & 0xFF) << 8) | (buffer[i] & 0xFF));
                                t[i / 2] = (short) (value << 3);
                            }
                            Log.e(TAG, Arrays.toString(t));
                            try {
                                ws.send(Arrays.toString(t));
                            } catch (Exception e) {
                                Log.e(TAG, e.toString());
                                //ws.reconnect();
                                stop();
                                showNetworkErrorDialog();
                            }
                        }
                        Log.e(TAG, "??????????????????");
                    }
                });
            }

            @Override
            public void onClose(int code, String reason, boolean remote) {
                Log.e(TAG, "????????????");
            }

            @Override
            public void onError(Exception e) {
                Log.e(TAG, e.toString());
                showNetworkErrorDialog();
            }
        };

        ws.connect();

    }

    private static void showNetworkErrorDialog() {
        MyApplication.tts.speek("??????????????????", true, true);
        new MessageDialog("??????????????????", "??????????????????????????????????????????????????????????????????", "??????", "??????")
                .setOkButton(new OnDialogButtonClickListener<MessageDialog>() {
                    @Override
                    public boolean onClick(MessageDialog baseDialog, View v) {
                        start();
                        return false;
                    }
                })
                .setCancelButton(new OnDialogButtonClickListener<MessageDialog>() {
                    @Override
                    public boolean onClick(MessageDialog baseDialog, View v) {
                        MyApplication.tts.speek("??????", true, true);
                        return false;
                    }
                }).show();
    }


    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
