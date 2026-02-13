# Django Blog Authentication - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Registration](#registration)
3. [Login](#login)
4. [Profile Management](#profile-management)
5. [Account Security](#account-security)
6. [Troubleshooting](#troubleshooting)
7. [FAQs](#faqs)

---

## Getting Started

### What You'll Need
- Web browser (Chrome, Firefox, Safari, Edge)
- Email address
- Strong password

### First Visit
1. Go to `http://localhost:8000` (or your site URL)
2. You'll see the Django Blog homepage
3. Click **"Register"** to create an account

---

## Registration

### Creating Your Account

#### Step 1: Access Registration Page
```
Click "Register" in the top navigation bar
URL: /register/
```

#### Step 2: Fill Out Registration Form
You'll see these fields:

**Username** (Required)
- Your unique login name
- 3-150 characters allowed
- Letters, numbers, @, ., +, -, and _ allowed
- Example: `john_doe` or `jane.smith2024`

**Email** (Required)
- Your email address
- Must be valid email format
- Must be unique (not used by another account)
- Example: `john@example.com`

**First Name** (Optional)
- Your first name
- Maximum 30 characters
- Example: `John`

**Last Name** (Optional)
- Your last name
- Maximum 150 characters
- Example: `Doe`

**Password** (Required)
- Your account password
- Minimum 8 characters
- Should include:
  - Uppercase letters (A-Z)
  - Lowercase letters (a-z)
  - Numbers (0-9)
  - Special characters (!@#$%^&*)
- Example: `SecurePass123!@#`

⚠️ **Password Tips:**
- Never use personal information (birthdate, name, phone)
- Avoid common passwords
- Use unique passwords for different websites
- Don't share your password

**Confirm Password** (Required)
- Re-enter your password exactly
- Must match the Password field

#### Step 3: Submit Registration
1. Review all information for accuracy
2. Click **"Register"** button
3. Wait for form processing

#### Step 4: Automatic Login
After successful registration:
- You'll be automatically logged in
- Redirected to your profile page
- **Congratulations!** Your account is ready to use

### What Happens Next
1. Your account is created in the system
2. Your profile is automatically set up
3. You can immediately access protected features
4. You're logged in for this session

---

## Login

### Logging Into Your Account

#### Step 1: Access Login Page
```
Click "Login" in top navigation
OR
Go to URL: /login/
```

#### Step 2: Enter Credentials
**Username** or **Email**
- Enter your username or registered email
- Example: `john_doe` or `john@example.com`

**Password**
- Enter your account password
- Characters are hidden for security

#### Step 3: Click Login
1. Review your information
2. Click **"Login"** button
3. Wait for authentication

#### Step 4: Access Your Profile
- On success: Redirected to `/profile/`
- On failure: Error message displayed
- Try again with correct credentials

### Staying Logged In

**Session Duration**
- Default: 2 weeks
- Auto-logout: 2 weeks of inactivity
- Always logout when using public computers

**Remember Me**
- Currently: Not available
- Future: "Remember me" option planned

### Logout

#### To Logout
1. Click **"Logout"** in top navigation
2. You'll be logged out immediately
3. Redirected to login page
4. Session is destroyed

**Security Note**: Always logout when:
- Using public or shared computer
- Finished browsing
- Before closing browser (on public devices)

---

## Profile Management

### Your Profile Page

#### Accessing Your Profile
```
Automatic: After login/registration
Manual: Click your username in navigation → /profile/
```

#### Profile Information Displayed

**Read-Only Information**
- Username: Your login name
- Member Since: Account creation date
- Joined Date: When you registered

**Editable Information**
- First Name
- Last Name
- Email
- Bio
- Location
- Website
- Profile Picture

### Updating Your Profile

#### Basic Information

**Step 1: Go to Profile Page**
- Click your username or navigate to `/profile/`

**Step 2: Fill in Edit Form**

**First Name** (Optional)
- Your given name
- Max 30 characters
- Example: `John`

**Last Name** (Optional)
- Your family name
- Max 150 characters
- Example: `Doe`

**Email** (Required)
- Must be valid email
- Must be unique (not used by another account)
- Used for account recovery
- Used for notifications

**Step 3: Save Changes**
1. Review all changes
2. Click **"Update Profile"** button
3. Wait for submission
4. Success message appears

#### Adding a Bio

**Step 1: Find Bio Field**
- Located on profile edit form
- Text area for longer text

**Step 2: Write Your Bio**
- Maximum 500 characters
- Describe yourself
- Include interests or expertise
- Example: "Web developer | Django enthusiast | Coffee lover ☕"

**Step 3: Save**
- Click "Update Profile"
- Bio is saved to your profile

#### Adding Location

**Step 1: Find Location Field**
- Text field on edit form

**Step 2: Enter Location**
- Your city or region
- Maximum 100 characters
- Example: "San Francisco, CA"

**Step 3: Save**
- Click "Update Profile"

#### Adding Website

**Step 1: Find Website Field**
- URL field on edit form

**Step 2: Enter Website URL**
- Full URL with https:// or http://
- Example: `https://mywebsite.com`
- Must be valid URL format

**Step 3: Save**
- Click "Update Profile"

#### Uploading Profile Picture

**Step 1: Click File Upload**
- Find "Profile Picture" field
- Click to select file

**Step 2: Choose Image File**
- Supported: JPG, PNG, GIF
- Recommended size: 200x200 pixels
- Max file size: 5MB
- Keep aspect ratio square

**Step 3: Preview (Optional)**
- Some browsers show preview
- Review before uploading

**Step 4: Save**
- Click "Update Profile"
- Image uploads and saves
- Displays on profile immediately

### Profile Picture Guidelines

✓ **Do**
- Use clear, professional photo
- Make sure face is visible
- Good lighting
- Simple background
- Square aspect ratio (1:1)

✗ **Don't**
- Use blurry images
- Use screenshots
- Multiple faces
- Offensive content
- Text or logos

---

## Account Security

### Password Management

#### Changing Your Password
*Note: Currently requires login each time. Future: Password change page planned.*

**Option 1: Manual Reset** (Future)
1. Go to Account Settings
2. Click "Change Password"
3. Enter current password
4. Enter new password (twice)
5. Save changes

**Option 2: Command Line** (Admin only)
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='yourname')
>>> user.set_password('newpassword123')
>>> user.save()
```

#### Password Best Practices

**Strong Passwords**
- ✓ 12+ characters for better security
- ✓ Mix of uppercase, lowercase, numbers, symbols
- ✓ No personal information
- ✓ Different for each website
- ✓ Regular updates (every 90 days)

**Weak Passwords to Avoid**
- ✗ Your name or username
- ✗ Common words (password, 123456)
- ✗ Sequential numbers (12345)
- ✗ Repeating characters (aaaa)
- ✗ Keyboard patterns (qwerty)

### Email Security

#### Email Verification (Future)
- Registration: Email verification planned
- Login alerts: Unusual login notifications planned
- Recovery: Password reset via email planned

#### Email Best Practices
- ✓ Use current, accessible email
- ✓ Check spam folder for notifications
- ✓ Keep email account secure
- ✓ Update email if it changes

### Security Features

#### CSRF Protection
- All forms protected against CSRF attacks
- Automatic token validation
- You don't need to do anything

#### Password Hashing
- Passwords never stored as plain text
- Uses industry-standard encryption (PBKDF2)
- Even admins cannot see your password

#### Session Security
- Session data encrypted
- Automatically expires after inactivity
- Session destroyed on logout

#### Login Security
- Generic error messages (no user enumeration)
- Failed login attempts tracked
- Future: Account lockout after failed attempts

### Privacy

#### Your Information
- **Public**: Username
- **Private**: Password, email (unless you share)
- **Limited**: Profile information (only to you)
- **Visible**: Bio, location, website (if filled)

#### Data Collection
- We collect: Username, email, profile data
- We don't sell: Your information
- We don't share: Personal data with third parties
- We store: Only what's necessary for service

---

## Troubleshooting

### Can't Register

#### Problem: "Username already exists"
**Cause**: Someone already has this username
**Solution**: Choose a different username
```
Try: john_doe2, johndoe_2024, john.d.2026
```

#### Problem: "Email already registered"
**Cause**: This email is associated with another account
**Solution 1**: Use different email address
**Solution 2**: If it's your email, you already have an account
```
Go to login and use password reset (future feature)
```

#### Problem: "Passwords don't match"
**Cause**: Password and confirmation don't match
**Solution**: 
1. Make sure Caps Lock is off
2. Type both passwords carefully
3. Avoid copy-paste if possible
4. Re-type both exactly the same

#### Problem: "Password too short/weak"
**Cause**: Password doesn't meet requirements
**Requirements**:
- Minimum 8 characters
- Mix of upper, lowercase, numbers
- Avoid common passwords
**Solution**: Create stronger password
```
Good: MyPass!2024#Secure
Bad:  password, 12345678
```

#### Problem: "Invalid email format"
**Cause**: Email doesn't look valid
**Solution**: Check email format
```
Correct: user@example.com
Wrong:   user@.com, @example.com, user@com
```

### Can't Login

#### Problem: "Invalid username or password"
**Cause**: Wrong username or password
**Solution**:
1. Check username spelling
2. Verify Caps Lock is off
3. Confirm password is correct
4. Try your email instead of username
5. Check for extra spaces

#### Problem: "Too many login attempts"
**Cause**: Multiple failed login attempts (future security feature)
**Solution**: Wait 15 minutes before trying again

#### Problem: "Account locked"
**Cause**: Account deactivated by admin
**Solution**: Contact support

### Can't Update Profile

#### Problem: "Email already in use"
**Cause**: Another account has this email
**Solution**: Use different email or use original

#### Problem: "Profile picture too large"
**Cause**: Image file exceeds size limit (5MB)
**Solution**: Compress image or use smaller file

#### Problem: "Invalid file type"
**Cause**: Uploaded file isn't an image (JPG/PNG)
**Solution**: Use JPG or PNG image file

#### Problem: "Invalid URL"
**Cause**: Website URL format incorrect
**Solution**: Use full URL
```
Correct: https://mysite.com
Wrong:   mysite.com, htp://mysite
```

### Session Issues

#### Problem: "Logged out unexpectedly"
**Cause**: Session expired (default 2 weeks inactivity)
**Solution**: Login again - this is normal

#### Problem: "Can't access profile"
**Cause**: Not logged in
**Solution**: Click "Login" and authenticate

#### Problem: "Changes didn't save"
**Cause**: CSRF token expired or network issue
**Solution**:
1. Refresh page
2. Try again
3. Check internet connection

---

## FAQs

### Account Questions

**Q: Can I change my username?**
A: Currently no. Would need admin to modify database.
Future: Username change feature planned.

**Q: Can I deactivate my account?**
A: Currently no. Would need admin assistance.
Future: Self-service account deletion planned.

**Q: Can I have multiple accounts?**
A: Technically yes, but email must be unique per account.
Recommended: Use one account per person.

**Q: What if I forget my password?**
A: Currently would need admin to reset.
Future: Password reset via email planned.

### Privacy Questions

**Q: Who can see my profile?**
A: Currently, only you (when logged in).
Future: Public profile viewing planned.

**Q: Is my email visible to others?**
A: No, email is private to you and admins.

**Q: Are my passwords secure?**
A: Yes, using industry-standard encryption (PBKDF2).
Even system administrators cannot see passwords.

**Q: How long is my session?**
A: Default 2 weeks of activity.
Auto-logout after 2 weeks of inactivity.

### Technical Questions

**Q: What if I get error after registration?**
A: Try these steps:
1. Refresh the page
2. Go to login and try logging in
3. If still issues, contact admin

**Q: Can I login from multiple devices?**
A: Yes, each device gets its own session.

**Q: What's "CSRF token"?**
A: Security feature that protects your account.
Auto-handled; you don't need to do anything.

**Q: Why is my password hidden when I type?**
A: Security feature to prevent shoulder surfing.
This is normal and protects your password.

### Account Recovery Questions

**Q: I can't login. What do I do?**
A: Contact your administrator for assistance.

**Q: I think my account is hacked. What do I do?**
A: 
1. Change your password immediately (if possible)
2. Don't use this account until resolved
3. Contact administrator

**Q: Can I delete my account?**
A: Contact administrator for account deletion.

---

## Tips & Tricks

### Security Tips
1. **Use unique passwords** - Don't reuse passwords
2. **Enable notifications** - Get alerts for unusual activity
3. **Logout regularly** - Especially on public computers
4. **Update information** - Keep email current
5. **Use strong passwords** - 12+ characters, mixed

### User Experience Tips
1. **Bookmark profile** - Quick access to `/profile/`
2. **Use username** - Easier to remember than email
3. **Complete profile** - Add bio and picture for better experience
4. **Check settings** - Review privacy settings regularly
5. **Read notifications** - Stay informed about your account

---

## Getting Help

### Support Channels
- Contact your site administrator
- Review documentation files
- Check troubleshooting section above

### Documentation Files
- [AUTH_README.md](AUTH_README.md) - Full system guide
- [QUICK_START.md](QUICK_START.md) - Getting started
- [SECURITY.md](SECURITY.md) - Security information
- [TESTING.md](TESTING.md) - How to test features

---

## Related Links

- [Main Application](http://localhost:8000)
- [Admin Panel](http://localhost:8000/admin)
- [Security Documentation](SECURITY.md)
- [Developer Guide](DEVELOPER_GUIDE.md)

---

**Last Updated**: February 2026
**Version**: 1.0
**Contact**: Site Administrator
