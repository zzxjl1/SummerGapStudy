package com.idealbroker.aisee;


import android.content.Context;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.Matrix;
import android.media.Image;
import android.os.Handler;
import android.os.Vibrator;
import android.util.Base64;
import android.util.Log;
import android.webkit.CookieManager;
import android.webkit.WebView;
import android.widget.Toast;

import org.opencv.core.Mat;
import org.opencv.imgproc.Imgproc;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.RandomAccessFile;
import java.io.UnsupportedEncodingException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.text.SimpleDateFormat;
import java.util.Collection;
import java.util.Date;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

public class ToolUtils {

    /**
     * 根据手机的分辨率从 dp 的单位 转成为 px(像素)
     */
    public static int dp2px(Context context, float dpValue) {
        final float scale = context.getResources().getDisplayMetrics().density;
        return (int) (dpValue * scale + 0.5f);
    }

    /**
     * 根据手机的分辨率从 px(像素) 的单位 转成为 dp
     */
    public static int px2dp(Context context, float pxValue) {
        final float scale = context.getResources().getDisplayMetrics().density;
        return (int) (pxValue / scale + 0.5f);
    }


    public static File moveFile(File file, File dir) throws IOException {
        File newFile = new File(dir, file.getName());
        FileChannel outputChannel = null;
        FileChannel inputChannel = null;
        try {
            outputChannel = new FileOutputStream(newFile).getChannel();
            inputChannel = new FileInputStream(file).getChannel();
            inputChannel.transferTo(0, inputChannel.size(), outputChannel);
            inputChannel.close();
            file.delete();
        } finally {
            if (inputChannel != null) inputChannel.close();
            if (outputChannel != null) outputChannel.close();
        }
        return newFile;
    }


    public static String FileToBase64(File file) {
        String path = file.getPath();
        InputStream is = null;
        byte[] data = null;
        String result = null;
        try {
            is = new FileInputStream(path);
            //创建一个字符流大小的数组。
            data = new byte[is.available()];
            //写入数组
            is.read(data);
            //用默认的编码格式进行编码
            result = Base64.encodeToString(data, Base64.NO_WRAP);
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            if (null != is) {
                try {
                    is.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
        return result;
    }


    public static String DateToString(long time) {
        Date d = new Date(time);
        SimpleDateFormat sf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        return sf.format(d);
    }

    /**
     * 删除单个文件
     *
     * @param filePath 被删除文件的文件名
     * @return 文件删除成功返回true，否则返回false
     */
    public static boolean deleteFile(String filePath) {
        File file = new File(filePath);
        if (file.isFile() && file.exists()) {
            return file.delete();
        }
        return false;
    }

    /**
     * 删除文件夹以及目录下的文件
     *
     * @param filePath 被删除目录的文件路径
     * @return 目录删除成功返回true，否则返回false
     */
    public static boolean deleteDirectory(String filePath) {
        boolean flag = false;
        //如果filePath不以文件分隔符结尾，自动添加文件分隔符
        if (!filePath.endsWith(File.separator)) {
            filePath = filePath + File.separator;
        }
        File dirFile = new File(filePath);
        if (!dirFile.exists() || !dirFile.isDirectory()) {
            return false;
        }
        flag = true;
        File[] files = dirFile.listFiles();
        //遍历删除文件夹下的所有文件(包括子目录)
        for (int i = 0; i < files.length; i++) {
            if (files[i].isFile()) {
                //删除子文件
                flag = deleteFile(files[i].getAbsolutePath());
                if (!flag) break;
            } else {
                //删除子目录
                flag = deleteDirectory(files[i].getAbsolutePath());
                if (!flag) break;
            }
        }
        if (!flag) return false;
        //删除当前空目录
        return dirFile.delete();
    }

    /**
     * 根据路径删除指定的目录或文件，无论存在与否
     *
     * @param filePath 要删除的目录或文件
     * @return 删除成功返回 true，否则返回 false。
     */
    public static boolean DeleteFolder(String filePath) {
        File file = new File(filePath);
        if (!file.exists()) {
            return false;
        } else {
            if (file.isFile()) {
                // 为文件时调用删除文件方法
                return deleteFile(filePath);
            } else {
                // 为目录时调用删除目录方法
                return deleteDirectory(filePath);
            }
        }
    }


    public static void showToastMessage(Context acticity, String text, int duration) {
        MyApplication.tts.speek(text, true, true);
        final Toast toast = Toast.makeText(acticity, text, Toast.LENGTH_SHORT);
        toast.show();
        Vibrator vibrator = (Vibrator)acticity.getSystemService(acticity.VIBRATOR_SERVICE);
        vibrator.vibrate(500);
        Handler handler = new Handler();
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                toast.cancel();
            }
        }, duration);
    }

    public static float getLocalVersion(Context ctx) {
        int localVersion = 0;
        try {
            PackageInfo packageInfo = ctx.getApplicationContext()
                    .getPackageManager()
                    .getPackageInfo(ctx.getPackageName(), 0);
            localVersion = packageInfo.versionCode;
            Log.d("TAG", "当前版本号：" + localVersion);
        } catch (PackageManager.NameNotFoundException e) {
            e.printStackTrace();
        }
        return localVersion;
    }

    public static void syncCookie(WebView webview) {

        CookieManager cookieManager = CookieManager.getInstance();
        cookieManager.removeAllCookies(null);
        cookieManager.setAcceptCookie(true);
        cookieManager.setAcceptFileSchemeCookies(true);
        cookieManager.setAcceptThirdPartyCookies(webview, true);
        cookieManager.setCookie(".idealbroker.cn", String.format("token=%s", MyApplication.user.getToken()));
        //cookieManager.setCookie("192.168.31.114:4000", String.format("token=%s", MyApplication.user.getToken()));
        cookieManager.flush();
        Log.e("cookie", String.format("get cookie info %s", cookieManager.getCookie("idealdoc.idealbroker.cn")));
        Log.e("COOKIE", MyApplication.user.getToken());

    }


    /**
     * 复制单个文件
     *
     * @param oldPath$Name String 原文件路径+文件名 如：data/user/0/com.test/files/abc.txt
     * @param newPath$Name String 复制后路径+文件名 如：data/user/0/com.test/cache/abc.txt
     * @return <code>true</code> if and only if the file was copied;
     * <code>false</code> otherwise
     */
    public static boolean copyFile(String oldPath$Name, String newPath$Name) {
        try {
            File oldFile = new File(oldPath$Name);
            FileInputStream fileInputStream = new FileInputStream(oldPath$Name);    //读入原文件
            FileOutputStream fileOutputStream = new FileOutputStream(newPath$Name);
            byte[] buffer = new byte[1024];
            int byteRead;
            while ((byteRead = fileInputStream.read(buffer)) != -1) {
                fileOutputStream.write(buffer, 0, byteRead);
            }
            fileInputStream.close();
            fileOutputStream.flush();
            fileOutputStream.close();
            Log.e("COPY FILE", "DONE");
            return true;
        } catch (Exception e) {
            Log.e("copy file error：", e.toString());
            return false;
        }
    }

    public static String genVuexStoreActionStr(String t) {
        return String.format("javascript:document.getElementById(\"app\").__vue_app__.config.globalProperties.$store.dispatch('%s')", t);
    }

    /**
     * 将字符串转成32 位MD5值
     *
     * @param string
     * @return
     */
    public static String String2MD5(String string) {
        byte[] hash;
        try {
            hash = MessageDigest.getInstance("MD5").digest(
                    string.getBytes("UTF-8"));
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
            return null;
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
            return null;
        }


        StringBuilder hex = new StringBuilder(hash.length * 2);
        for (byte b : hash) {
            if ((b & 0xFF) < 0x10)
                hex.append("0");
            hex.append(Integer.toHexString(b & 0xFF));

        }

        return hex.toString();// 32位
        //return hex.toString().toString().substring(8, 24);// 16位
    }

    public static Bitmap resizeBitmap(Bitmap bitmap, int w, int h) {
        int width = bitmap.getWidth();
        int height = bitmap.getHeight();

        float scaleWidth = ((float) w) / width;
        float scaleHeight = ((float) h) / height;

        Matrix matrix = new Matrix();
        matrix.postScale(scaleWidth, scaleHeight);

        Bitmap resizedBitmap = Bitmap.createBitmap(bitmap, 0, 0, width,
                height, matrix, true);
        return resizedBitmap;
    }

    public static Bitmap Mat2Bitmap(Mat img) {
        Bitmap bmp = Bitmap.createBitmap(img.width(), img.height(), Bitmap.Config.RGB_565);
        org.opencv.android.Utils.matToBitmap(img, bmp);
        return bmp;
    }

    public static Mat resizeMat(Mat image, float w, float h) {
        org.opencv.core.Size size = new org.opencv.core.Size(w, h);
        Mat img2 = new Mat(size, image.type());
        Imgproc.resize(image, img2, img2.size());
        return img2;
    }


    // This value is 2 ^ 18 - 1, and is used to clamp the RGB values before their ranges
    // are normalized to eight bits.
    static final int MAX_CHANNEL_VALUE = 262143;

    static class yuv_frame {
        byte[][] yuvBytes;
        int[] argbArray;
        int yPlane_RowStride;
        int uPlane_RowStride;
        int uPlane_PixelStride;
        int width;
        int height;
    }

    public static yuv_frame saveyuvCameraImage(Image imageProxy) {
        yuv_frame frame = new yuv_frame();
        Image.Plane yPlane = imageProxy.getPlanes()[0];
        Image.Plane uPlane = imageProxy.getPlanes()[1];

        frame.width = imageProxy.getWidth();
        frame.height = imageProxy.getHeight();

        frame.yuvBytes = new byte[3][];
        frame.argbArray = new int[frame.width * frame.height];
        for (int i = 0; i < imageProxy.getPlanes().length; i++) {
            final ByteBuffer buffer = imageProxy.getPlanes()[i].getBuffer();
            frame.yuvBytes[i] = new byte[buffer.capacity()];
            buffer.get(frame.yuvBytes[i]);
        }
        frame.yPlane_RowStride = yPlane.getRowStride();
        frame.uPlane_RowStride = uPlane.getRowStride();
        frame.uPlane_PixelStride = uPlane.getPixelStride();
        return frame;
    }

    public static Bitmap yuvCameraImageToBitmap(Image imageProxy) {

        yuv_frame frame = saveyuvCameraImage(imageProxy);

        convertYUV420ToARGB8888_java(
                frame.yuvBytes[0],
                frame.yuvBytes[1],
                frame.yuvBytes[2],
                frame.argbArray,
                frame.width,
                frame.height,
                frame.yPlane_RowStride,
                frame.uPlane_RowStride,
                frame.uPlane_PixelStride
        );

       /* convertYUV420ToARGB8888(
                frame.yuvBytes[0],
                frame.yuvBytes[1],
                frame.yuvBytes[2],
                frame.argbArray,
                frame.width,
                frame.height,
                frame.yPlane_RowStride,
                frame.uPlane_RowStride,
                frame.uPlane_PixelStride,
                false
        );*/

        return Bitmap.createBitmap(frame.argbArray, frame.width, frame.height, Bitmap.Config.ARGB_8888);
    }

    public static Bitmap yuvCameraImageToBitmap(yuv_frame frame) {

        convertYUV420ToARGB8888_java(
                frame.yuvBytes[0],
                frame.yuvBytes[1],
                frame.yuvBytes[2],
                frame.argbArray,
                frame.width,
                frame.height,
                frame.yPlane_RowStride,
                frame.uPlane_RowStride,
                frame.uPlane_PixelStride
        );

        return Bitmap.createBitmap(frame.argbArray, frame.width, frame.height, Bitmap.Config.ARGB_8888);
    }

    public static void convertYUV420ToARGB8888_java(
            byte[] yData,
            byte[] uData,
            byte[] vData,
            int[] out,
            int width,
            int height,
            int yRowStride,
            int uvRowStride,
            int uvPixelStride) {
        int yp = 0;
        for (int j = 0; j < height; j++) {
            int pY = yRowStride * j;
            int pUV = uvRowStride * (j >> 1);

            for (int i = 0; i < width; i++) {
                int uvOffset = pUV + (i >> 1) * uvPixelStride;
                out[yp++] = yuv2Rgb(0xff & yData[pY + i], 0xff & uData[uvOffset], 0xff & vData[uvOffset]);
            }
        }
    }

    private static int yuv2Rgb(int y, int u, int v) {
        // Adjust and check YUV values
        y = (y - 16) < 0 ? 0 : (y - 16);
        u -= 128;
        v -= 128;

        // This is the floating point equivalent. We do the conversion in integer
        // because some Android devices do not have floating point in hardware.
        // nR = (int)(1.164 * nY + 2.018 * nU);
        // nG = (int)(1.164 * nY - 0.813 * nV - 0.391 * nU);
        // nB = (int)(1.164 * nY + 1.596 * nV);
        int y1192 = 1192 * y;
        int r = (y1192 + 1634 * v);
        int g = (y1192 - 833 * v - 400 * u);
        int b = (y1192 + 2066 * u);

        // Clipping RGB values to be inside boundaries [ 0 , MAX_CHANNEL_VALUE ]
        r = r > MAX_CHANNEL_VALUE ? MAX_CHANNEL_VALUE : Math.max(r, 0);
        g = g > MAX_CHANNEL_VALUE ? MAX_CHANNEL_VALUE : Math.max(g, 0);
        b = b > MAX_CHANNEL_VALUE ? MAX_CHANNEL_VALUE : Math.max(b, 0);

        return 0xff000000 | ((r << 6) & 0xff0000) | ((g >> 2) & 0xff00) | ((b >> 10) & 0xff);
    }


}
