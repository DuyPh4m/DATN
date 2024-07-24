package com.example.myapp;

import androidx.annotation.NonNull;
import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.neurosky.connection.ConnectionStates;
import com.neurosky.connection.EEGPower;
import com.neurosky.connection.TgStreamHandler;
import com.neurosky.connection.TgStreamReader;
import com.neurosky.connection.DataType.MindDataType;

import android.Manifest;
import android.app.Activity;
import android.bluetooth.BluetoothAdapter;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.util.Log;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import com.example.myapp.R;
import org.json.JSONException;
import org.json.JSONObject;
import java.io.IOException;
import java.io.PrintWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import org.json.JSONException;
import org.json.JSONObject;
import java.io.IOException;
import java.io.PrintWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@RequiresApi(api = Build.VERSION_CODES.R)
public class LabelActivity extends AppCompatActivity implements AdapterView.OnItemSelectedListener {

    private static final int REQUEST_EXTERNAL_STORAGE = 1;
    private static final String[] PERMISSIONS_STORAGE = {
            Manifest.permission.READ_EXTERNAL_STORAGE,
            Manifest.permission.WRITE_EXTERNAL_STORAGE,
            Manifest.permission.MANAGE_EXTERNAL_STORAGE,
    };

    @RequiresApi(api = Build.VERSION_CODES.S)
    public void verifyPermission(Activity activity) {
        // Get permission status
        int permission = ActivityCompat.checkSelfPermission(activity, Manifest.permission.MANAGE_EXTERNAL_STORAGE);
        if (permission != PackageManager.PERMISSION_GRANTED) {
            // We don't have permission we request it
            ActivityCompat.requestPermissions(
                    activity,
                    PERMISSIONS_STORAGE,
                    REQUEST_EXTERNAL_STORAGE
            );
        }
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                requestPermissions(new String[]{Manifest.permission.BLUETOOTH_CONNECT}, 99);
            }
        }
    }

    private static final String TAG = LabelActivity.class.getSimpleName();
    private TgStreamReader tgStreamReader;
    private BluetoothAdapter mBluetoothAdapter;
    private TextView tv_label_notification = null;
    private int badPacketCount = 0;
    private Button btn_start;
    private Button btn_stop;
    private Button btn_finish;
    private String currentStatus = "Buồn ngủ";
    private String IP;
    private static boolean isPoorSignal = false;
    private static boolean isLabeling = false;

    private ExecutorService executorService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        setContentView(R.layout.label_view);

        IP = getString(R.string.IP);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            verifyPermission(LabelActivity.this);
        }

        initView();
        executorService = Executors.newFixedThreadPool(2);

        try {
            mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
            if (mBluetoothAdapter == null || !mBluetoothAdapter.isEnabled()) {
                Toast.makeText(
                        this,
                        "Vui lòng bật Bluetooth",
                        Toast.LENGTH_LONG).show();
                finish();
            }
        } catch (Exception e) {
            e.printStackTrace();
            Log.i(TAG, "error:" + e.getMessage());
            return;
        }

        tgStreamReader = new TgStreamReader(mBluetoothAdapter, callback);
        tgStreamReader.setGetDataTimeOutTime(6);
        tgStreamReader.startLog();
    }

    private void initView() {
        tv_label_notification = findViewById(R.id.tv_label_notification);
        tv_label_notification.setText("Nhấn nút để bắt đầu");

        btn_start = findViewById(R.id.btn_start_label);
        btn_stop = findViewById(R.id.btn_stop_label);
        btn_finish = findViewById(R.id.btn_finish_label);
        // init spinner and set listener
        Spinner status = findViewById(R.id.label_spinner);
        status.setOnItemSelectedListener(this);

        btn_stop.setEnabled(false);

        btn_start.setOnClickListener(arg0 -> {
            if (isLabeling) {
                return;
            }
            btn_start.setEnabled(false);
            btn_finish.setEnabled(false);
            btn_stop.setEnabled(true);
            badPacketCount = 0;

            if (tgStreamReader != null) {
                // Prepare for connecting
                tgStreamReader.stop();
                                tgStreamReader.close();
                                tgStreamReader.connect();
                                isLabeling = true;
                                startLabelActivity();
                            // Import statements

                            public class LabelActivity extends AppCompatActivity implements AdapterView.OnItemSelectedListener {

                                private static final String TAG = LabelActivity.class.getSimpleName();
                                private static final int MSG_UPDATE_BAD_PACKET = 1001;
                                private static final int MSG_UPDATE_STATE = 1002;

                                private Button startButton;
                                private Button stopButton;
                                private Button finishButton;
                                private TextView labelNotificationTextView;
                                private Spinner spinner;

                                private boolean isLabeling = false;
                                private boolean isPoorSignal = false;
                                private int badPacketCount = 0;
                                private String currentStatus = "";

                                private ExecutorService executorService;
                                private TgStreamReader tgStreamReader;

                                private final Handler linkDetectedHandler = new Handler(Looper.getMainLooper()) {
                                    @Override
                                    public void handleMessage(Message msg) {
                                        switch (msg.what) {
                                            case MindDataType.CODE_MEDITATION:
                                                Log.d(TAG, "MindDataType.CODE_MEDITATION " + msg.arg1);
                                                break;
                                            case MindDataType.CODE_ATTENTION:
                                                Log.d(TAG, "CODE_ATTENTION " + msg.arg1);
                                                break;
                                            case MindDataType.CODE_EEGPOWER:
                                                if (isPoorSignal) {
                                                    isPoorSignal = false;
                                                    break;
                                                }
                                                EEGPower power = (EEGPower) msg.obj;
                                                if (power.isValidate()) {
                                                    sendEEGDataToServer(power);
                                                }
                                                break;
                                            case MindDataType.CODE_POOR_SIGNAL:
                                                int poorSignal = msg.arg1;
                                                Log.d(TAG, "poorSignal:" + poorSignal);
                                                if (poorSignal > 0) {
                                                    isPoorSignal = true;
                                                }
                                                break;
                                            public class LabelActivity extends AppCompatActivity implements AdapterView.OnItemSelectedListener {
                                                private static final String TAG = LabelActivity.class.getSimpleName();
                                                private static final String IP = "your_server_ip_address";

                                                private Button startButton;
                                                private Button stopButton;
                                                private Button finishButton;
                                                private TextView labelNotificationTextView;
                                                private Spinner spinner;

                                                private ExecutorService executorService;
                                                private TgStreamReader tgStreamReader;
                                                private boolean isLabeling = false;
                                                private String currentStatus;

                                                private final Handler handler = new Handler() {
                                                    @Override
                                                    public void handleMessage(@NonNull Message msg) {
                                                        switch (msg.what) {
                                                            // Handle messages
                                                            default:
                                                                break;
                                                        }
                                                        super.handleMessage(msg);
                                                    }
                                                };

                                                @Override
                                                protected void onCreate(Bundle savedInstanceState) {
                                                    super.onCreate(savedInstanceState);
                                                    setContentView(R.layout.activity_label);

                                                    initializeViews();
                                                    setListeners();

                                                    executorService = Executors.newSingleThreadExecutor();
                                                    tgStreamReader = new TgStreamReader();

                                                    labelNotificationTextView.setText("Nhấn nút để bắt đầu");
                                                }

                                                private void initializeViews() {
                                                    startButton = findViewById(R.id.btn_start);
                                                    stopButton = findViewById(R.id.btn_stop);
                                                    finishButton = findViewById(R.id.btn_finish);
                                                    labelNotificationTextView = findViewById(R.id.tv_label_notification);
                                                    spinner = findViewById(R.id.spinner);
                                                }

                                                private void setListeners() {
                                                    startButton.setOnClickListener(arg0 -> startLabelActivity());
                                                    stopButton.setOnClickListener(arg0 -> stop());
                                                    finishButton.setOnClickListener(arg0 -> {
                                                        finishLabelActivity();
                                                        finish();
                                                    });
                                                    spinner.setOnItemSelectedListener(this);
                                                public class LabelActivity extends AppCompatActivity implements AdapterView.OnItemSelectedListener {
                                                    private static final String TAG = LabelActivity.class.getSimpleName();
                                                    private static final String IP = "your_server_ip_address";

                                                    private TextView labelNotificationTextView;
                                                    private Spinner statusSpinner;
                                                    private ExecutorService executorService;
                                                    private String currentStatus;

                                                    @Override
                                                    protected void onCreate(Bundle savedInstanceState) {
                                                        super.onCreate(savedInstanceState);
                                                        setContentView(R.layout.activity_label);

                                                        labelNotificationTextView = findViewById(R.id.labelNotificationTextView);
                                                        statusSpinner = findViewById(R.id.statusSpinner);
                                                        statusSpinner.setOnItemSelectedListener(this);

                                                        executorService = Executors.newSingleThreadExecutor();
                                                    }

                                                    private void startLabelActivity() {
                                                        executorService.execute(() -> {
                                                            runOnUiThread(() -> {
                                                                labelNotificationTextView.setText("Đang khởi tạo...");
                                                                showToast("Đang kết nối...", Toast.LENGTH_SHORT);
                                                            });

                                                            try {
                                                                URL url = new URL("http://" + IP + ":5000/api/pre_labeling");
                                                                HttpURLConnection urlConnection = (HttpURLConnection) url.openConnection();
                                                                urlConnection.setDoOutput(true);
                                                                urlConnection.setRequestMethod("POST");
                                                                urlConnection.setRequestProperty("Content-Type", "application/json");

                                                                int responseCode = urlConnection.getResponseCode();
                                                                if (responseCode != HttpURLConnection.HTTP_OK) {
                                                                    Log.e(TAG, "Failed to send request to server: " + responseCode);
                                                                } else {
                                                                    runOnUiThread(() -> {
                                                                        showToast("Khởi tạo thành công", Toast.LENGTH_SHORT);
                                                                        stopButton.setEnabled(true);
                                                                        labelNotificationTextView.setText("Đang gán nhãn");
                                                                    });
                                                                }
                                                                urlConnection.disconnect();
                                                            } catch (IOException e) {
                                                                e.printStackTrace();
                                                            }
                                                        });
                                                    }

                                                    private void finishLabelActivity() {
                                                        executorService.execute(() -> {
                                                            try {
                                                                URL url = new URL("http://" + IP + ":5000/api/stop_labeling");
                                                                HttpURLConnection urlConnection = (HttpURLConnection) url.openConnection();
                                                                urlConnection.setDoOutput(true);
                                                                urlConnection.setRequestMethod("POST");
                                                                urlConnection.setRequestProperty("Content-Type", "application/json");

                                                                int responseCode = urlConnection.getResponseCode();
                                                                if (responseCode != HttpURLConnection.HTTP_OK) {
                                                                    Log.e(TAG, "Failed to send request to server: " + responseCode);
                                                                } else {
                                                                    isLabeling = false;
                                                                }
                                                                urlConnection.disconnect();
                                                            } catch (IOException e) {
                                                                e.printStackTrace();
                                                            }
                                                        });
                                                    }

                                                    public void stop() {
                                                        if (tgStreamReader != null) {
                                                            tgStreamReader.stop();
                                                            tgStreamReader.close();
                                                        }
                                                        isLabeling = false;
                                                        labelNotificationTextView.setText("Nhấn nút để bắt đầu");
                                                    }

                                                    @Override
                                                    protected void onDestroy() {
                                                        stop();
                                                        super.onDestroy();
                                                    }

                                                    @Override
                                                    public void onBackPressed() {
                                                        finishLabelActivity();
                                                        super.onBackPressed();
                                                    }

                                                    @Override
                                                    protected void onStop() {
                                                        stop();
                                                        super.onStop();
                                                    }

                                                    @Override
                                                    protected void onResume() {
                                                        labelNotificationTextView.setText("Nhấn nút để bắt đầu");
                                                        super.onResume();
                                                    }

                                                    private void showToast(final String msg, final int timeStyle) {
                                                        runOnUiThread(() -> Toast.makeText(getApplicationContext(), msg, timeStyle).show());
                                                    }

                                                    private void sendEEGDataToServer(EEGPower power) {
                                                        executorService.execute(() -> {
                                                            try {
                                                                URL url = new URL("http://" + IP + ":5000/api/labeling");
                                                                HttpURLConnection urlConnection = (HttpURLConnection) url.openConnection();
                                                                urlConnection.setDoOutput(true);
                                                                urlConnection.setRequestMethod("POST");
                                                                urlConnection.setRequestProperty("Content-Type", "application/json");

                                                                JSONObject jsonParam = getJsonObject(power);

                                                                try (PrintWriter printWriter = new PrintWriter(urlConnection.getOutputStream())) {
                                                                    printWriter.print(jsonParam);
                                                                }

                                                                int responseCode = urlConnection.getResponseCode();
                                                                if (responseCode != HttpURLConnection.HTTP_OK) {
                                                                    Log.e(TAG, "Failed to send data to server: " + responseCode);
                                                                }
                                                                urlConnection.disconnect();
                                                            } catch (IOException | JSONException e) {
                                                                e.printStackTrace();
                                                            }
                                                        });
                                                    }

                                                    @NonNull
                                                    private JSONObject getJsonObject(EEGPower data) throws JSONException {
                                                        int label = "Buồn ngủ".equals(currentStatus) ? 1 : 0;
                                                        JSONObject jsonParam = new JSONObject();
                                                        JSONObject value = new JSONObject();
                                                        value.put("delta", data.delta);
                                                        value.put("theta", data.theta);
                                                        value.put("low_alpha", data.lowAlpha);
                                                        value.put("high_alpha", data.highAlpha);
                                                        value.put("low_beta", data.lowBeta);
                                                        value.put("high_beta", data.highBeta);
                                                        value.put("low_gamma", data.lowGamma);
                                                        value.put("middle_gamma", data.middleGamma);
                                                        value.put("classification", label);
                                                        jsonParam.put("value", value);
                                                        return jsonParam;
                                                    }

                                                    // Spinner related methods
                                                    @Override
                                                    public void onItemSelected(AdapterView<?> parent, View view, int pos, long id) {
                                                        currentStatus = parent.getItemAtPosition(pos).toString();
                                                    }

                                                    @Override
                                                    public void onNothingSelected(AdapterView<?> parent) {
                                                    }
                                                }
