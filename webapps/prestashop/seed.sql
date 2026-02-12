-- Note: Prestashop is automatically seeded with demo data, which is sufficiently deterministic for our use case.

-- Orders (5): Awaiting payment (3), Payment error (1), Canceled (1); each with random items and subtotal
-- Catalog (19): Clothes (2), Accessories (11), Art (7)
-- Attributes (4): Size, Color, Dimensions, Paper Type
-- Brands (2): Graphic Corner, Studio Design
-- Suppliers (2): Accessories Supplier, Fashion Supplier
-- Customers (3)


SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;

INSERT INTO `ps_configuration` VALUES (425,NULL,NULL,'PS_CART_FOLLOWING','1','YYYY-MM-DD 11:10:57','YYYY-MM-DD 11:10:57');

INSERT INTO `ps_wishlist` VALUES (1,3,1,1,'2C89AAE20B5ECE11','My wishlist',NULL,'YYYY-MM-DD 08:48:36','YYYY-MM-DD 08:48:36',1);

INSERT INTO `ps_wishlist_product` VALUES (2,1,7,0,1,1);
INSERT INTO `ps_wishlist_product` VALUES (3,1,6,0,1,1);
INSERT INTO `ps_wishlist_product` VALUES (4,1,8,0,1,1);
INSERT INTO `ps_wishlist_product` VALUES (5,1,10,24,1,1);

INSERT INTO `ps_cart` VALUES (6,1,1,0,'',1,0,0,1,3,4,'f35db51726a9675b45f9a9f7ccb6c2c5',0,0,'',0,0,'YYYY-MM-DD 10:37:17','YYYY-MM-DD 10:42:46',NULL);

INSERT INTO `ps_cart_product` VALUES (6,1,0,1,1,0,1,'YYYY-MM-DD 10:40:52');
INSERT INTO `ps_cart_product` VALUES (6,2,0,1,9,0,1,'YYYY-MM-DD 10:42:27');
INSERT INTO `ps_cart_product` VALUES (6,10,0,1,25,0,1,'YYYY-MM-DD 10:42:16');
INSERT INTO `ps_cart_product` VALUES (6,16,0,1,28,0,1,'YYYY-MM-DD 10:42:05');

-- Disable FK checks (orders & history reference this table)
SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE ps_order_state;

INSERT INTO ps_order_state VALUES
(1,0,0,'ps_checkpayment','#34209E',1,0,0,0,0,0,0,0,0),
(2,1,0,'','#3498D8',1,0,1,0,0,1,1,0,0),
(3,1,0,'','#3498D8',1,0,1,1,0,1,0,0,0),
(4,1,0,'','#01B887',1,0,1,1,1,1,0,0,0),
(5,1,0,'','#01B887',1,0,1,1,1,1,0,0,0),
(6,0,0,'','#2C3E50',1,0,0,0,0,0,0,0,0),
(7,1,0,'','#01B887',1,0,0,0,0,0,0,0,0),
(8,0,0,'','#E74C3C',1,0,0,0,0,0,0,0,0),
(9,1,0,'','#3498D8',1,0,0,0,0,1,0,0,0),
(10,0,0,'ps_wirepayment','#34209E',1,0,0,0,0,0,0,0,0),
(11,1,0,'','#3498D8',1,0,1,0,0,1,0,0,0),
(12,0,0,'','#34209E',1,0,0,0,0,0,0,0,0),
(13,0,0,'ps_cashondelivery','#34209E',1,0,0,0,0,0,0,0,0);

-- Re-enable FK checks
SET FOREIGN_KEY_CHECKS = 1;