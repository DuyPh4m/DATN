package com.example.myapp;

import android.content.Context;
import android.content.res.Configuration;
import android.graphics.Bitmap;
import android.graphics.Bitmap.Config;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.PorterDuff;
import android.graphics.PorterDuffXfermode;
import android.util.AttributeSet;
import android.util.Log;
import android.view.View;

public class DrawWaveView extends View {
    private static final String TAG = "DrawWaveView";
    private Path path;
    private Paint paint;
    private int viewWidth;
    private int viewHeight;
    private Bitmap cacheBitmap;
    private Canvas cacheCanvas;
    private Paint bmpPaint;
    private int maxPoint;
    private int currentPoint;
    private int maxValue;
    private int minValue;
    private float x;
    private float y;
    private float preX;
    private float preY;
    private boolean restart;

    private int bottom;
    private int height;
    private int left;
    private int width;

    private float pixPerHeight;
    private float pixPerWidth;

    public DrawWaveView(Context context) {
        super(context);
        init();
    }

    public DrawWaveView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    private void init() {
        path = new Path();
        paint = new Paint(Paint.DITHER_FLAG);
        bmpPaint = new Paint();
        cacheBitmap = null;
        cacheCanvas = null;
        maxPoint = 0;
        currentPoint = 0;
        maxValue = 0;
        minValue = 0;
        x = 0;
        y = 0;
        preX = 0;
        preY = 0;
        restart = true;
        bottom = 0;
        height = 0;
        left = 0;
        width = 0;
        pixPerHeight = 0;
        pixPerWidth = 0;
    }

    public void setValue(int maxPoint, int maxValue, int minValue) {
        this.maxPoint = maxPoint;
        this.maxValue = maxValue;
        this.minValue = minValue;
    }

    public void initView() {
        bottom = getBottom();
        width = getWidth();
        left = getLeft();
        height = getHeight();

        pixPerHeight = (float) height / (maxValue - minValue);
        pixPerWidth = (float) width / maxPoint;
        cacheBitmap = Bitmap.createBitmap(width, height, Config.ARGB_8888);
        cacheCanvas = new Canvas();
        cacheCanvas.setBitmap(cacheBitmap);

        paint.setColor(Color.parseColor("#1976D2"));
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(4);
        paint.setAntiAlias(true);
        paint.setDither(true);
        currentPoint = 0;
    }

    public void clear() {
        Paint clearPaint = new Paint();
        clearPaint.setXfermode(new PorterDuffXfermode(PorterDuff.Mode.CLEAR));
        cacheCanvas.drawPaint(clearPaint);
        clearPaint.setXfermode(new PorterDuffXfermode(PorterDuff.Mode.SRC));
        currentPoint = 0;
        path.reset();
        invalidate();
    }

    public boolean isReady() {
        return initFlag;
    }

    public void updateData(int data) {
        if (!initFlag) {
            return;
        }
        y = translateDataToY(data);
        x = translatePointToX(currentPoint);
        if (currentPoint == 0) {
            path.moveTo(x, y);
            currentPoint++;
            preX = x;
            preY = y;
        } else if (currentPoint == maxPoint) {
            cacheCanvas.drawPath(path, paint);
            currentPoint = 0;
        } else {
            path.quadTo(preX, preY, x, y);
            currentPoint++;
            preX = x;
            preY = y;
        }
        invalidate();
        if (currentPoint == 0) {
            clear();
        }
    }

    private float translateDataToY(int data) {
        return (float) bottom - (data - minValue) * pixPerHeight;
    }

    private float translatePointToX(int point) {
        return (float) left + point * pixPerWidth;
    }

    private boolean initFlag = false;

    @Override
    protected void onDraw(Canvas canvas) {
        canvas.drawBitmap(cacheBitmap, 0, 0, bmpPaint);
        canvas.drawPath(path, paint);
    }

    @Override
    protected void onConfigurationChanged(Configuration newConfig) {
        super.onConfigurationChanged(newConfig);
        initFlag = false;
        Log.d(TAG, "onConfigurationChanged");
    }

    @Override
    protected void onAttachedToWindow() {
        super.onAttachedToWindow();
        Log.d(TAG, "onAttachedToWindow");
        initFlag = false;
    }

    @Override
    protected void onLayout(boolean changed, int left, int top, int right, int bottom) {
        super.onLayout(changed, left, top, right, bottom);
        Log.d(TAG, "onLayout");
        if (!initFlag) {
            initView();
            initFlag = true;
        }
    }
}
