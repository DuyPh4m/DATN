package com.example.myapp;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.Switch;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.auth.AuthResult;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseAuthInvalidCredentialsException;
import com.google.firebase.auth.FirebaseAuthUserCollisionException;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.firestore.FirebaseFirestore;

import java.util.HashMap;
import java.util.Map;

public class SignUpActivity extends AppCompatActivity {
    private static final String TAG = "SignUpActivity";
    private static final String ADMIN_CODE = "20204737";
    private FirebaseAuth mAuth;
    private EditText emailEditText, passwordEditText, fullnameEditText, genderEditText, birthdayEditText, adminCodeEditText;
    private Switch adminSwitch;
    private FirebaseFirestore db;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_sign_up);

        mAuth = FirebaseAuth.getInstance();
        db = FirebaseFirestore.getInstance();

        initializeViews();
        setupAdminSwitch();
        setupSignUpButton();
    }

    private void initializeViews() {
        emailEditText = findViewById(R.id.emailField);
        passwordEditText = findViewById(R.id.passwordField);
        fullnameEditText = findViewById(R.id.fullname);
        genderEditText = findViewById(R.id.gender);
        birthdayEditText = findViewById(R.id.birthdate);
        adminSwitch = findViewById(R.id.adminSwitch);
        adminCodeEditText = findViewById(R.id.adminCode);
        adminCodeEditText.setVisibility(View.GONE);
    }

    private void setupAdminSwitch() {
        adminSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                adminCodeEditText.setVisibility(isChecked ? View.VISIBLE : View.GONE);
            }
        });
    }

    private void setupSignUpButton() {
        Button signUpButton = findViewById(R.id.signUpButton);
        signUpButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String email = emailEditText.getText().toString();
                String password = passwordEditText.getText().toString();
                String fullname = fullnameEditText.getText().toString();
                String gender = genderEditText.getText().toString();
                String birthday = birthdayEditText.getText().toString();
                String adminCode = adminCodeEditText.getText().toString();

                if (adminSwitch.isChecked() && !adminCode.equals(ADMIN_CODE)) {
                    Toast.makeText(SignUpActivity.this, "Invalid admin code", Toast.LENGTH_SHORT).show();
                    return;
                }

                mAuth.createUserWithEmailAndPassword(email, password)
                        .addOnCompleteListener(SignUpActivity.this, new OnCompleteListener<AuthResult>() {
                            @Override
                            public void onComplete(@NonNull Task<AuthResult> task) {
                                if (task.isSuccessful()) {
                                    FirebaseUser user = mAuth.getCurrentUser();
                                    assert user != null;
                                    updateUserInfo(user.getUid(), fullname, birthday, gender, adminSwitch.isChecked() ? "admin" : "user");
                                    Toast.makeText(SignUpActivity.this, "Sign up successful!", Toast.LENGTH_SHORT).show();
                                    startActivity(new Intent(SignUpActivity.this, adminSwitch.isChecked() ? AdminMainActivity.class : UserMainActivity.class));
                                } else {
                                    if (task.getException() instanceof FirebaseAuthUserCollisionException) {
                                        Toast.makeText(SignUpActivity.this, "This email is already registered!", Toast.LENGTH_SHORT).show();
                                    } else if (task.getException() instanceof FirebaseAuthInvalidCredentialsException) {
                                        Toast.makeText(SignUpActivity.this, "Invalid email or password", Toast.LENGTH_SHORT).show();
                                    } else {
                                        Toast.makeText(SignUpActivity.this, "Sign up failed", Toast.LENGTH_SHORT).show();
                                    }
                                }
                            }
                        });
            }
        });
    }

    private void updateUserInfo(String userId, String name, String birthday, String gender, String role) {
        Map<String, Object> user = new HashMap<>();
        user.put("userId", userId);
        user.put("name", name);
        user.put("birthday", birthday);
        user.put("gender", gender);
        user.put("role", role);

        db.collection("Brainwave").document(userId)
                .set(user)
                .addOnSuccessListener(aVoid -> Log.d(TAG, "DocumentSnapshot successfully written!"))
                .addOnFailureListener(e -> Log.w(TAG, "Error writing document", e));
    }
}