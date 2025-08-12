<?php

require dirname(__FILE__) . '/../config/config.inc.php';
require_once _PS_CLASS_DIR_ . 'Customer.php';

// Prevent duplicate creation
if (Customer::getCustomersByEmail('auto.customer@example.com')) {
    echo "Customer already exists.\n";
    exit;
}

$customer = new Customer();
$customer->firstname = 'Auto';
$customer->lastname = 'Customer';
$customer->email = 'auto.customer@example.com';
$customer->passwd = md5(_COOKIE_KEY_.'mypassword'); // PrestaShop hash
$customer->active = 1;
$customer->add();

echo "Customer created successfully.\n";