# Flower Shop Project Documentation

> **Note**: This is a school project.

## Overview

This project is a PHP-based flower shop web application with:

- A public storefront and landing page
- User registration and login
- Separate user and admin dashboards
- Product management for administrators
- Cart, checkout, and payment-related pages
- Feedback and order management pages

The app is built to run in a local PHP environment such as XAMPP and uses MySQL for storage.

## Tech Stack

- PHP
- MySQL
- HTML, CSS, and JavaScript
- Bootstrap 5
- Font Awesome and Boxicons
- Composer dependency: `guzzlehttp/guzzle`

## Project Structure

Important files and folders in the root of the project:

- `index.html` - Public homepage and login modal
- `register.php` - User registration page
- `login.php` - Authentication handler
- `logout.php` - Session logout handler
- `user_dashboard.php` - Logged-in user homepage
- `user_product_dashboard.php` - User product browsing page
- `admin_dashboard.php` - Admin product management dashboard
- `admin_orders.php` - Admin order management page
- `manage_users.php` - Admin user management page
- `cart.php` - Shopping cart page
- `checkout.php` - Checkout page
- `product_detail.php` - Product detail page
- `purchase_item.php` - Purchase flow handler
- `payment_success.php` - Successful payment page
- `payment_cancelled.php` - Cancelled payment page
- `payment_failed.php` - Failed payment page
- `create_payment.php` - Payment creation endpoint
- `create_gcash_payment.php` - GCash payment endpoint
- `paymongo_webhook.php` - Payment webhook handler
- `submit_feedback.php` - Feedback submission handler
- `view_feedbacks.php` - Admin feedback viewer
- `add_item.php`, `edit_item.php`, `delete_item.php` - Product management handlers
- `add_user.php`, `edit_user.php`, `delete_user.php` - User management handlers
- `src/` - Frontend assets and styles
- `image/` - Site images and branding assets
- `uploads/` - Uploaded files or product images
- `vendor/` - Composer dependencies

## Features

### Public Site

- Home page with hero carousel and featured products
- Navigation links for products, blog, about, and contact sections
- Login modal with username/password form
- Registration page for new users

### User Area

- Personalized dashboard after login
- Product browsing
- Cart and checkout flow
- Order history page
- Payment result pages

### Admin Area

- Protected admin dashboard
- Product listing with update and delete actions
- Order management
- Customer management
- Feedback review
- Link to Google Analytics

## Authentication Flow

The login flow is handled in `login.php`:

- The submitted username is looked up in the `users` table
- The stored password hash is checked with `password_verify()`
- The session stores the username and role
- Admin users are redirected to `admin_dashboard.php`
- Regular users are redirected to `user_dashboard.php`

Registration is handled in `register.php`:

- A new username is checked against the database
- Passwords are hashed before storage
- Duplicate usernames are rejected

## Database Setup

The database connection is defined in `db.php`.

Default local settings:

- Host: `localhost`
- Username: `root`
- Password: empty
- Database: `flowershopdb`

Make sure the `flowershopdb` database exists before running the app.

### Expected Tables

Based on the code, the application expects tables such as:

- `users`
- `items`
- Possibly order, feedback, and payment-related tables depending on the rest of your schema

If your database schema differs, update the SQL queries in the relevant PHP files.

## Local Setup

1. Install XAMPP or another PHP + MySQL stack.
2. Copy the project folder into your web server directory.
3. Start Apache and MySQL.
4. Create a database named `flowershopdb`.
5. Import your SQL schema if you already have one.
6. Run `composer install` in the project root if dependencies are not already installed.
7. Open the project in your browser through localhost.

Example local URL:

```text
http://localhost/Flower%20shop/
```

## Composer Dependencies

The project currently requires:

```json
{
  "require": {
    "guzzlehttp/guzzle": "^7.9"
  }
}
```

If you need to reinstall dependencies:

```bash
composer install
```

## Payment Integration

The repository includes payment-related endpoints and callbacks:

- `create_payment.php`
- `create_gcash_payment.php`
- `paymongo_webhook.php`
- `payment_success.php`
- `payment_cancelled.php`
- `payment_failed.php`

These files suggest the app is wired for external payment processing, likely through a PayMongo-style flow.

## Notes

- Some files reference assets or pages that may need cleanup if they are renamed later.
- Several pages use shared UI libraries from CDNs, so internet access is needed for those assets unless you bundle them locally.
- `dashboard.html` appears to be an older or separate dashboard template and is not the main authenticated dashboard used by `login.php`.

## Suggested Next Steps

- Add a database schema document or SQL export
- Add screenshots of the storefront and dashboards
- Add an admin/user flow diagram
- Add deployment notes for XAMPP or hosting
