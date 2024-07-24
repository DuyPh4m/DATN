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
import com.google.firebase.firestore.DocumentReference;
import com.google.firebase.firestore.FirebaseFirestore;

public class UserMainActivity extends AppCompatActivity {

    private static final int BLUETOOTH_SCAN_PERMISSION_REQUEST_CODE = 99;
    private FirebaseAuth firebaseAuth;
    private FirebaseFirestore firebaseFirestore;

    private FirebaseUser currentUser;
    private CardView monitorCardView;
    private CardView classifyCardView;

    @RequiresApi(api = Build.VERSION_CODES.S)
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_user_main);

        firebaseAuth = FirebaseAuth.getInstance();
        firebaseFirestore = FirebaseFirestore.getInstance();
        currentUser = firebaseAuth.getCurrentUser();

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_SCAN) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.BLUETOOTH_SCAN}, BLUETOOTH_SCAN_PERMISSION_REQUEST_CODE);
        }

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        monitorCardView = findViewById(R.id.monitorCard);
        classifyCardView = findViewById(R.id.classifyCard);

        monitorCardView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(UserMainActivity.this, MonitorActivity.class);
                startActivity(intent);
            }
        });

        classifyCardView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(UserMainActivity.this, ClassifyActivity.class);
                startActivity(intent);
            }
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
            popupMenu.getMenuInflater().inflate(R.menu.menu_profile, popupMenu.getMenu()); // menu_profile contains your options
            popupMenu.show();
            popupMenu.setOnMenuItemClickListener(menuItem -> {
                int itemId = menuItem.getItemId();
                if (itemId == R.id.signOut_item) {// Sign out
                    FirebaseAuth.getInstance().signOut();
                    // Redirect to login
                    Intent intent = new Intent(UserMainActivity.this, SignInActivity.class);
                    startActivity(intent);
                    finish();
                    return true;
                } else if (itemId == R.id.updateInfo_item) {// Handle update info
                    Intent updateInfoIntent = new Intent(UserMainActivity.this, UpdateInfoActivity.class);
                    startActivity(updateInfoIntent);
                    return true;
                }
                return false;
            });
            return true;
        }
        return super.onOptionsItemSelected(item);
    }
}