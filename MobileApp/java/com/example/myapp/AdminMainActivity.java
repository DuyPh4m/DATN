package com.example.myapp;

import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.PopupMenu;
import androidx.cardview.widget.CardView;
import androidx.core.content.ContextCompat;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;

import androidx.appcompat.widget.Toolbar;

import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.firestore.FirebaseFirestore;

public class AdminMainActivity extends AppCompatActivity {

    private static final int BLUETOOTH_SCAN_PERMISSION_REQUEST_CODE = 99;
    private FirebaseAuth firebaseAuth;
    private FirebaseFirestore firebaseFirestore;

    private FirebaseUser currentUser;
    private CardView monitorCardView;
    private CardView classifyCardView;
    private CardView labelCardView;
    private CardView trainCardView;

    @RequiresApi(api = Build.VERSION_CODES.S)
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_admin_main);

        firebaseAuth = FirebaseAuth.getInstance();
        firebaseFirestore = FirebaseFirestore.getInstance();
        currentUser = firebaseAuth.getCurrentUser();

        setupPermissions();
        setupViews();
        setupClickListeners();
    }

    private void setupPermissions() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_SCAN) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.BLUETOOTH_SCAN}, BLUETOOTH_SCAN_PERMISSION_REQUEST_CODE);
        }
    }

    private void setupViews() {
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        monitorCardView = findViewById(R.id.monitorCard);
        classifyCardView = findViewById(R.id.classifyCard);
        labelCardView = findViewById(R.id.labelCard);
        trainCardView = findViewById(R.id.trainCard);
    }

    private void setupClickListeners() {
        monitorCardView.setOnClickListener(view -> {
            startActivity(new Intent(AdminMainActivity.this, MonitorActivity.class));
        });

        classifyCardView.setOnClickListener(view -> {
            startActivity(new Intent(AdminMainActivity.this, ClassifyActivity.class));
        });

        labelCardView.setOnClickListener(view -> {
            startActivity(new Intent(AdminMainActivity.this, LabelActivity.class));
        });

        trainCardView.setOnClickListener(view -> {
            startActivity(new Intent(AdminMainActivity.this, TrainActivity.class));
        });
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        if (item.getItemId() == R.id.action_profile) {
            View menuItemView = findViewById(R.id.action_profile); // Same ID as menu item
            PopupMenu popupMenu = new PopupMenu(this, menuItemView);
            popupMenu.getMenuInflater().inflate(R.menu.menu_profile, popupMenu.getMenu()); // menu_profile contains options
            popupMenu.show();
            popupMenu.setOnMenuItemClickListener(menuItem -> {
                int itemId = menuItem.getItemId();
                if (itemId == R.id.signOut_item) {// Sign out
                    FirebaseAuth.getInstance().signOut();
                    // Redirect to login
                    startActivity(new Intent(AdminMainActivity.this, SignInActivity.class));
                    finish();
                    return true;
                } else if (itemId == R.id.updateInfo_item) {// Handle update info
                    startActivity(new Intent(AdminMainActivity.this, UpdateInfoActivity.class));
                    return true;
                }
                return false;
            });
            return true;
        }
        return super.onOptionsItemSelected(item);
    }
}
