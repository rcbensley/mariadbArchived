CREATE TABLE IF NOT EXISTS products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(32) NOT NULL
) ENGINE=InnoDB;

INSERT INTO products (product_name) VALUES 
    ("Toaster Gen 1"),
    ("Toaster 5000"),
    ("Toaster 5001"),
    ("Toast-it-2k"),
    ("Bread Burner"),
    ("Bread Burner 2: Crumpets"),
    ("Toaster Classic"),
    ("Toaster Pro")
;


CREATE TABLE IF NOT EXISTS orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    invoice_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    INDEX idx_invoice (invoice_id)
) ENGINE=InnoDB;