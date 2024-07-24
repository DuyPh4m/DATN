package com.example.myapp;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.myapp.databinding.ActivityUpdateInfoBinding;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.auth.UserProfileChangeRequest;
import com.google.firebase.firestore.DocumentReference;
import com.google.firebase.firestore.FirebaseFirestore;

public class UpdateInfoActivity extends AppCompatActivity {

    private EditText nameEditText;
    private EditText emailEditText;
    private Button updateButton;

    private FirebaseAuth firebaseAuth;
    private FirebaseFirestore firebaseFirestore;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_update_info);

        firebaseAuth = FirebaseAuth.getInstance();
        firebaseFirestore = FirebaseFirestore.getInstance();

        nameEditText = findViewById(R.id.editTextName);
        emailEditText = findViewById(R.id.editTextEmail);
        updateButton = findViewById(R.id.buttonUpdate);

        updateButton.setOnClickListener(v -> {
            String name = nameEditText.getText().toString();
            String email = emailEditText.getText().toString();

            updateUserProfile(name, email);
        });
    }

    private void updateUserProfile(String name, String email) {
        FirebaseUser user = firebaseAuth.getCurrentUser();
        if (user != null) {
            UserProfileChangeRequest profileUpdates = new UserProfileChangeRequest.Builder()
                    .setDisplayName(name)
                    .build();
            user.updateProfile(profileUpdates)
                    .addOnCompleteListener(task -> {
                        if (task.isSuccessful()) {
                            updateUserInfoInDatabase(user.getUid(), name, email);
                        }
                    });
        }
    }

    private void updateUserInfoInDatabase(String userId, String name, String email) {
        DocumentReference userRef = firebaseFirestore.collection("Brainwave").document(userId);
        userRef.update("name", name, "email", email)
                .addOnSuccessListener(aVoid -> {
                    Toast.makeText(UpdateInfoActivity.this, "User info updated", Toast.LENGTH_SHORT).show();
                })
                .addOnFailureListener(e -> {
                    Toast.makeText(UpdateInfoActivity.this, "Error updating user info", Toast.LENGTH_SHORT).show();
                });
    }
}