SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';

INSERT INTO `ps_address` VALUES (7,11,270,0,0,3,0,'supplier','','supplier','supplier','Nishi-Shinjuku 1-25-1','','','Tokyo','','090-1234-5678','','','','2025-09-29 10:46:52','2025-09-29 10:46:52',1,0);

INSERT INTO `ps_customer` VALUES (3,1,1,1,3,1,0,NULL,NULL,NULL,'Jones','Jonathan','test@test.com','$2y$10$vGm9PHZuakY0yN4sodgAsOT7i1zqSLUs7xudXua6nFsNPnGFWRolq','2025-09-30 21:31:40','2003-01-01',0,NULL,'0000-00-00 00:00:00',0,NULL,0.000000,0,0,'aa7ef13e058d57f5c118a6680f36bf68',NULL,1,0,0,'2025-10-01 03:31:40','2025-10-01 03:31:40',NULL,'0000-00-00 00:00:00');
INSERT INTO `ps_customer_group` VALUES (3,1);
INSERT INTO `ps_customer_group` VALUES (3,2);


INSERT INTO `ps_attribute_group` VALUES (5,0,'select',4);
INSERT INTO `ps_attribute_group_lang` VALUES (5,1,'Weight','Weight');
INSERT INTO `ps_attribute_group_shop` VALUES (5,1);

INSERT INTO `ps_category` VALUES (10,2,1,2,17,20,1,'2025-09-29 10:46:36','2025-09-29 10:46:36',3,0);
INSERT INTO `ps_category` VALUES (11,10,1,3,18,19,1,'2025-09-29 10:46:39','2025-09-29 10:46:39',0,0);
INSERT INTO `ps_category_group` VALUES (10,1);
INSERT INTO `ps_category_group` VALUES (10,2);
INSERT INTO `ps_category_group` VALUES (10,3);
INSERT INTO `ps_category_group` VALUES (11,1);
INSERT INTO `ps_category_group` VALUES (11,2);
INSERT INTO `ps_category_group` VALUES (11,3);
INSERT INTO `ps_category_lang` VALUES (10,1,1,'Shoes','<p>Description</p>','','shoes','','','');
INSERT INTO `ps_category_lang` VALUES (11,1,1,'Sports shoes','<p>Description</p>','','sports-shoes','','','');
INSERT INTO `ps_category_product` VALUES (2,20,20);
INSERT INTO `ps_category_product` VALUES (9,20,8);
INSERT INTO `ps_category_shop` VALUES (10,1,3);
INSERT INTO `ps_category_shop` VALUES (11,1,0);

INSERT INTO `ps_feature` VALUES (3,2);
INSERT INTO `ps_feature_lang` VALUES (3,1,'Season');
INSERT INTO `ps_feature_shop` VALUES (3,1);

INSERT INTO `ps_manufacturer` VALUES (3,'Nike','2025-09-29 10:46:32','2025-09-29 10:46:32',1);
INSERT INTO `ps_manufacturer_lang` VALUES (3,1,'<p>Description</p>','','','','');
INSERT INTO `ps_manufacturer_shop` VALUES (3,1);

INSERT INTO `ps_product` VALUES (20,2,2,2,1,0,0,0,'','','','',0.000000,0,1,0,0,9.000000,5.490000,'',0.000000,0.000000,0.000000,'test1','test1','',0.000000,0.000000,0.000000,0.000000,2,1,0,0,0,0,0,'default',0,1,'0000-00-00',0,'new',1,0,'both',0,0,1,0,'2025-09-29 10:46:43','2025-09-29 10:46:47',0,3,1,'virtual');
INSERT INTO `ps_product_lang` VALUES (20,1,1,'<p>Description</p>','<p>Vector graphic, format: svg. Download for personal, private and non-commercial use.</p>','bird-vector-graphics','','','','bird','','','','');
INSERT INTO `ps_product_shop` VALUES (20,1,2,0,0,0,0.000000,1,0,0,9.000000,5.490000,'',0.000000,0.000000,0.000000,0,0,0,0,'default',0,1,'0000-00-00',0,'new',1,0,'both',0,0,'2025-09-29 10:46:43','2025-09-29 10:46:47',3);
INSERT INTO `ps_product_supplier` VALUES (74,20,0,2,'test1',5.490000,1);
INSERT INTO `ps_product_supplier` VALUES (75,20,0,1,'test1',6.490000,1);

INSERT INTO `ps_stock_available` VALUES (59,20,0,1,0,300,300,0,0,1,'');
INSERT INTO `ps_stock_mvt` VALUES (1,59,NULL,NULL,11,1,'Doe','John',300,'2025-09-29 10:46:47',1,0.000000,0.000000,0.000000,NULL);

INSERT INTO `ps_supplier` VALUES (3,'Shoes supplier','2025-09-29 10:46:52','2025-09-29 10:46:52',1);
INSERT INTO `ps_supplier_lang` VALUES (3,1,'','','','');
INSERT INTO `ps_supplier_shop` VALUES (3,1);