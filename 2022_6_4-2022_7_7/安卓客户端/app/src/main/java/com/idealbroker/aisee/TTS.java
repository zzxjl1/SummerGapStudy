package com.idealbroker.aisee;

import static com.idealbroker.aisee.ToolUtils.String2MD5;

import android.media.MediaPlayer;
import android.os.Environment;
import android.util.Log;

import com.kongzue.baseokhttp.HttpRequest;
import com.kongzue.baseokhttp.listener.OnDownloadListener;
import com.kongzue.baseokhttp.listener.ResponseListener;
import com.kongzue.baseokhttp.util.Parameter;

import java.io.File;
import java.io.IOException;
import java.util.LinkedList;
import java.util.Queue;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

public class TTS {

    String TAG = "TTS PLAYER";
    MediaPlayer mp = new MediaPlayer();
    LinkedList queue = new LinkedList();
    Executor mExecutor = Executors.newSingleThreadExecutor();

    {
        mExecutor.execute(new Runnable() {
            @Override
            public void run() {
                while (true) {
                    try {
                        Thread.sleep(100);
                        //Log.e(TAG,"reading queue");
                        if (!queue.isEmpty() && !mp.isPlaying()) {
                            File f = (File) queue.removeFirst();
                            play(f);
                        }

                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }
        });
    }

    private void play(File f) {
        try {
            mp.reset();
            mp.setDataSource(f.getAbsolutePath());
            mp.prepare();
            mp.start();
        } catch (IOException e) {
            Log.e(TAG, "播放失败");
        }
    }

    private void download_handler(File f, boolean preemptive, boolean flush_queue) {
        if (flush_queue) queue.clear();
        if (preemptive) {
            play(f);
        } else {
            queue.addLast(f);
        }

    }

    public void stop() {
        queue.clear();
        mp.reset();
    }

    public void speek(String text, boolean preemptive, boolean flush_queue) {

        if (text.isEmpty()) return;
        String url = String.format("/tts?text=%s", text);
        File base_path = new File(MyApplication.context.getCacheDir().getPath(), "tts");
        base_path.mkdir();
        File path = new File(base_path, String2MD5(url) + ".wav");
        if (path.exists()) {
            Log.e(TAG, "命中缓存");
            download_handler(path, preemptive, flush_queue);
            return;
        }
        HttpRequest.DOWNLOAD(
                MyApplication.context,
                url,
                path,
                new OnDownloadListener() {
                    @Override
                    public void onDownloadSuccess(File file) {
                        Log.e(TAG, "文件已下载完成");
                        download_handler(file, preemptive, flush_queue);
                    }

                    @Override
                    public void onDownloading(int progress) {
                        Log.e(TAG, "PROGRESS：" + progress);
                    }

                    @Override
                    public void onDownloadFailed(Exception e) {
                        Log.e(TAG, e.toString());
                    }
                }
        );

    }
}
