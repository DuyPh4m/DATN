package com.example.myapp;

import static com.example.myapp.MonitorActivity.MSG_UPDATE_BAD_PACKET;
import static com.example.myapp.MonitorActivity.MSG_UPDATE_STATE;

import androidx.annotation.NonNull;
import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;

import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.neurosky.connection.ConnectionStates;
import com.neurosky.connection.EEGPower;
import com.neurosky.connection.TgStreamHandler;
import com.neurosky.connection.TgStreamReader;
import com.neurosky.connection.DataType.MindDataType;

import android.Manifest;
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

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class ClassifyActivity extends AppCompatActivity implements AdapterView.OnItemSelectedListener {
    private static final String TAG = ClassifyActivity.class.getSimpleName();
    private TgStreamReader tgStreamReader;
    private BluetoothAdapter mBluetoothAdapter;
    private TextView tv_classify_result;
    private TextView tv_classify_notification;
    private int badPacketCount = 0;
    private Button btn_start;
    private Button btn_stop;
    private Button btn_finish;

    private static boolean isPoorSignal = false;
    private static boolean isClassifying = false;
    private String currentModel = "RandomForest";
    private String IP;
    private FirebaseUser user;
    private ExecutorService executorService;

    @RequiresApi(api = Build.VERSION_CODES.S)
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                requestPermissions(new String[]{Manifest.permission.BLUETOOTH_CONNECT}, 99);
            }
        }
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        setContentView(R.layout.classify_view);

        FirebaseAuth firebaseAuth = FirebaseAuth.getInstance();
        user = firebaseAuth.getCurrentUser();
        IP = getString(R.string.IP);

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
        tv_classify_result = findViewById(R.id.tv_classify_result);
        tv_classify_notification = findViewById(R.id.tv_classify_notification);

        btn_start = findViewById(R.id.btn_start_classify);
        btn_stop = findViewById(R.id.btn_stop_classify);
        btn_finish = findViewById(R.id.btn_finish_classify);

        Spinner models = findViewById(R.id.models_spinner);
        models.setOnItemSelectedListener(this);

        btn_stop.setEnabled(false);

        btn_start.setOnClickListener(arg0 -> {
            if (isClassifying) {
                return;
            }
            btn_start.setEnabled(false);
            btn_stop.setEnabled(true);
            btn_finish.setEnabled(false);

            if (tgStreamReader != null) {
                tgStreamReader.stop();
                tgStreamReader.close();
                tgStreamReader.connect();
                isClassifying = true;
                if ("Bắt đầu".equals(btn_start.getText().toString())) {
                    startClassifyActivity();
                }
                tv_classify_notification.setText("Đang đánh giá");
            } else {
                stop();
                showToast("Kết nối thất bại!\nVui lòng kiểm tra lại thiết bị", Toast.LENGTH_SHORT);
                btn_start.setEnabled(true);
                btn_finish.setEnabled(true);
                btn_stop.setEnabled(false);
            }

        });

        btn_stop.setOnClickListener(arg0 -> {
            stop();
            btn_start.setText("Tiếp tục");
            btn_start.setEnabled(true);
            btn_stop.setEnabled(false);
            btn_finish.setEnabled(true);
            tv_classify_notification.setText("Nhấn nút để bắt đầu");
        });

        btn_finish.setOnClickListener(arg0 -> {
            finishClassifyActivity();
            finish();
        });
    }

    private void startClassifyActivity() {
        executorService.execute(() -> {
            runOnUiThread(() -> {
                tv_classify_notification.setText("Đang khởi tạo...");
                // Show a toast message
                showToast("Đang kết nối...", Toast.LENGTH_SHORT);

                // Connect to the server and send a POST request
                try {
                    URL url = new URL("http://" + IP + ":5000/api/pre_classify");
                    HttpURLConnection urlConnection = (HttpURLConnection) url.openConnection();
                    urlConnection.setDoOutput(true);
                    urlConnection.setRequestMethod("POST");
                    urlConnection.setRequestProperty("Content-Type", "application/json");

                    // Create a JSON object with user_id and model_name
                    JSONObject jsonObject = new JSONObject();
                    jsonObject.put("user_id", user.getUid());
                    jsonObject.put("model_name", currentModel);

                    // Send the JSON object as the request body
                    PrintWriter printWriter = new PrintWriter(urlConnection.getOutputStream());
                    printWriter.print(jsonObject);
                    printWriter.close();

                    // Get the response code
                    int responseCode = urlConnection.getResponseCode();
                    if (responseCode != HttpURLConnection.HTTP_OK) {
                        Log.e(TAG, "Failed to send request to server: " + responseCode);
                    } else {
                        isClassifying = false;
                        runOnUiThread(() -> {
                            showToast("Khởi tạo thành công", Toast.LENGTH_SHORT);
                            btn_stop.setEnabled(true);
                            tv_classify_notification.setText("Đang đánh giá");
                        });
                    }
                    urlConnection.disconnect();
                } catch (IOException | JSONException e) {
                    e.printStackTrace();
                }

                // Finish the classify activity
                private void finishClassifyActivity() {
                    executorService.execute(() -> {
                        try {
                            URL url = new URL("http://" + IP + ":5000/api/stop_classify");
                            HttpURLConnection urlConnection = (HttpURLConnection) url.openConnection();
                            urlConnection.setDoOutput(true);
                                                        urlConnection.setRequestMethod("POST");
                                                        urlConnection.setRequestProperty("Content-Type", "application/json");

                                                        int responseCode = urlConnection.getResponseCode();
                                                        if (responseCode != HttpURLConnection.HTTP_OK) {
                                                            Log.e(TAG, "Failed to send request to server: " + responseCode);
                                                        } else {
                                                            isClassifying = false;
                                                        }
                                                        urlConnection.disconnect();
                                                    } catch (IOException e) {
                                                        e.printStackTrace();
                                                    }
                                                });
                                            }

                                            // Stop the classification process
                                            public void stop() {
                                                if (tgStreamReader != null) {
                                                    tgStreamReader.stop();
                                                    tgStreamReader.close();
                                                }
                                                tvClassifyResult.setText("--");
                                                isClassifying = false;
                                                tvClassifyNotification.setText("Nhấn nút để bắt đầu");
                                            }

                                            // Clean up resources when the activity is destroyed
                                            @Override
                                            protected void onDestroy() {
                                                stop();
                                                super.onDestroy();
                                            }

                                            // Clean up resources when the activity is stopped
                                            @Override
                                            protected void onStop() {
                                                stop();
                                                super.onStop();
                                            }

                                            // Handle the back button press
                                            @Override
                                            public void onBackPressed() {
                                                finishClassifyActivity();
                                                super.onBackPressed();
                                            }

                                            // Resume the activity
                                            @Override
                                            protected void onResume() {
                                                tvClassifyNotification.setText("Nhấn nút để bắt đầu");
                                                super.onResume();
                                            }

                                            // Handle the callback from the ThinkGear stream
                                            private final TgStreamHandler callback = new TgStreamHandler() {
                                                @Override
                                                public void onStatesChanged(int connectionStates) {
                                                    Log.d(TAG, "connectionStates change to: " + connectionStates);
                                                    switch (connectionStates) {
                                                        case ConnectionStates.STATE_CONNECTED:
                                                            tgStreamReader.start();
                                                            showToast("Đã kết nối", Toast.LENGTH_SHORT);
                                                            break;
                                                        case ConnectionStates.STATE_WORKING:
                                                            tgStreamReader.startRecordRawData();
                                                            break;
                                                        case ConnectionStates.STATE_GET_DATA_TIME_OUT:
                                                            tgStreamReader.stopRecordRawData();
                                                            showToast("Không nhận được dữ liệu", Toast.LENGTH_SHORT);
                                                            break;
                                                        case ConnectionStates.STATE_FAILED:
                                                            setFailState();
                                                            showToast("Kết nối thất bại!\nVui lòng kiểm tra lại thiết bị", Toast.LENGTH_SHORT);
                                                            break;
                                                        default:
                                                            break;
                                                    public class ClassifyActivity extends AppCompatActivity implements AdapterView.OnItemSelectedListener {

                                                        private static final String TAG = "ClassifyActivity";
                                                        private static final int MSG_UPDATE_STATE = 1;
                                                        private static final int MSG_UPDATE_BAD_PACKET = 2;

                                                        private boolean isPoorSignal = false;
                                                        private int badPacketCount = 0;
                                                        private String currentModel;
                                                        private TGStreamReader tgStreamReader;

                                                        private TextView tvClassifyResult;

                                                        @Override
                                                        protected void onCreate(Bundle savedInstanceState) {
                                                            super.onCreate(savedInstanceState);
                                                            setContentView(R.layout.activity_classify);

                                                            // Initialize views
                                                            tvClassifyResult = findViewById(R.id.tvClassifyResult);
                                                            Spinner spinner = findViewById(R.id.spinner);

                                                            // Set item selection listener for the spinner
                                                            spinner.setOnItemSelectedListener(this);

                                                            // Create a TGStreamReader
                                                            tgStreamReader = createTGStreamReader();

                                                            // Start the TGStreamReader
                                                            tgStreamReader.start();
                                                        }

                                                        private TGStreamReader createTGStreamReader() {
                                                            TGStreamReader tgStreamReader = new TGStreamReader(this, callback);
                                                            tgStreamReader.setGetDataTimeOutTime(5);
                                                            return tgStreamReader;
                                                        }

                                                        private final TgStreamHandler callback = new TgStreamHandler() {
                                                            @Override
                                                            public void onStatesChanged(int connectionStates) {
                                                                Message msg = linkDetectedHandler.obtainMessage();
                                                                msg.what = MSG_UPDATE_STATE;
                                                                msg.arg1 = connectionStates;
                                                                linkDetectedHandler.sendMessage(msg);
                                                            }

                                                            @Override
                                                            public void onRecordFail(int flag) {
                                                                Log.e(TAG, "onRecordFail: " + flag);
                                                            }

                                                            @Override
                                                            public void onChecksumFail(byte[] payload, int length, int checksum) {
                                                                badPacketCount++;
                                                                Message msg = linkDetectedHandler.obtainMessage();
                                                                msg.what = MSG_UPDATE_BAD_PACKET;
                                                                msg.arg1 = badPacketCount;
                                                                linkDetectedHandler.sendMessage(msg);
                                                            }

                                                            @Override
                                                            public void onDataReceived(int datatype, int data, Object obj) {
                                                                Message msg = linkDetectedHandler.obtainMessage();
                                                                msg.what = datatype;
                                                                msg.arg1 = data;
                                                                msg.obj = obj;
                                                                linkDetectedHandler.sendMessage(msg);
                                                            }
                                                        };

                                                        private final Handler linkDetectedHandler = new Handler(Looper.getMainLooper()) {
                                                            @Override
                                                            public void handleMessage(Message msg) {
                                                                switch (msg.what) {
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
                                                                            sendEEGDataToBackend(power);
                                                                        }
                                                                        break;
                                                                    case MindDataType.CODE_POOR_SIGNAL:
                                                                        int poorSignal = msg.arg1;
                                                                        Log.d(TAG, "poorSignal:" + poorSignal);
                                                                        if (poorSignal > 0) {
                                                                            isPoorSignal = true;
                                                                        }
                                                                        break;
                                                                    default:
                                                                        break;
                                                                }
                                                                super.handleMessage(msg);
                                                            }
                                                        };

                                                        private void sendEEGDataToBackend(EEGPower power) {
                                                            new Thread(() -> {
                                                                try {
                                                                    URL url = new URL("http://" + IP + ":5000/api/classify");
                                                                    HttpURLConnection urlConnection = (HttpURLConnection) url.openConnection();
                                                                    urlConnection.setDoOutput(true);
                                                                    urlConnection.setRequestMethod("POST");
                                                                    urlConnection.setRequestProperty("Content-Type", "application/json");

                                                                    // Build a JSON object with user_id and EEG power values
                                                                    JSONObject jsonParam = buildJsonObject(power);

                                                                    // Send the JSON object as the request body
                                                                    try (PrintWriter printWriter = new PrintWriter(urlConnection.getOutputStream())) {
                                                                        printWriter.print(jsonParam);
                                                                    }

                                                                    int responseCode = urlConnection.getResponseCode();
                                                                    if (responseCode == HttpURLConnection.HTTP_OK) {
                                                                        // Read the response
                                                                        InputStream in = new BufferedInputStream(urlConnection.getInputStream());
                                                                        String result = org.apache.commons.io.IOUtils.toString(in, StandardCharsets.UTF_8);
                                                                        JSONObject jsonObject = new JSONObject(result);

                                                                        // Assuming your response contains a status field
                                                                        int currentStatus = jsonObject.getInt("status");

                                                                        // Update the UI based on the current status
                                                                        runOnUiThread(() -> {
                                                                            String label = currentStatus == 0 ? "Tập trung" : "Buồn ngủ";
                                                                            tvClassifyResult.setText(label);
                                                                        });

                                                                        in.close();
                                                                    }
                                                                    urlConnection.disconnect();
                                                                } catch (Exception e) {
                                                                    Log.e(TAG, "Error sending data to backend", e);
                                                                }
                                                            }).start();
                                                        }

                                                        @NonNull
                                                        private JSONObject buildJsonObject(EEGPower power) throws JSONException {
                                                            JSONObject jsonParam = new JSONObject();
                                                            jsonParam.put("user_id", user.getUid());
                                                            JSONObject value = new JSONObject();
                                                            value.put("delta", power.delta);
                                                            value.put("theta", power.theta);
                                                            value.put("high_alpha", power.highAlpha);
                                                            value.put("low_alpha", power.lowAlpha);
                                                            value.put("high_beta", power.highBeta);
                                                            value.put("low_beta", power.lowBeta);
                                                            value.put("low_gamma", power.lowGamma);
                                                            value.put("middle_gamma", power.middleGamma);
                                                            jsonParam.put("value", value);
                                                            return jsonParam;
                                                        }

                                                        public void showToast(final String msg, final int timeStyle) {
                                                            ClassifyActivity.this.runOnUiThread(() -> Toast.makeText(getApplicationContext(), msg, timeStyle).show());
                                                        }

                                                        private void setFailState() {
                                                            runOnUiThread(() -> {
                                                                if (tgStreamReader != null) {
                                                                    tgStreamReader.stop();
                                                                    tgStreamReader.close();
                                                                }
                                                            });
                                                        }

                                                        @Override
                                                        public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                                                            currentModel = parent.getItemAtPosition(position).toString();
                                                        }

                                                        @Override
                                                        public void onNothingSelected(AdapterView<?> parent) {

                                                        }
                                                    }
