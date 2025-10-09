SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
INSERT INTO `ps_address` VALUES (7,11,270,0,0,3,0,'supplier','','supplier','supplier','Nishi-Shinjuku 1-25-1','','','Tokyo','','090-1234-5678','','','','2025-10-09 13:38:49','2025-10-09 13:38:49',1,0);

INSERT INTO `ps_admin_filter` VALUES (1,1,1,'','','{\"limit\":20,\"orderBy\":\"id_product\",\"sortOrder\":\"desc\",\"filters\":[]}','product');

INSERT INTO `ps_admin_filter` VALUES (2,1,1,'','','{\"limit\":50,\"orderBy\":\"date_add\",\"sortOrder\":\"DESC\",\"filters\":[]}','customer');

INSERT INTO `ps_admin_filter` VALUES (3,1,1,'','','{\"limit\":10,\"orderBy\":\"name\",\"sortOrder\":\"asc\",\"filters\":[]}','manufacturer');

INSERT INTO `ps_admin_filter` VALUES (4,1,1,'','','{\"limit\":10,\"orderBy\":\"id_address\",\"sortOrder\":\"desc\",\"filters\":[]}','manufacturer_address');

INSERT INTO `ps_admin_filter` VALUES (5,1,1,'','','{\"orderBy\":\"position\",\"sortOrder\":\"asc\",\"limit\":50,\"filters\":{\"id_category_parent\":10}}','category');

INSERT INTO `ps_admin_filter` VALUES (6,1,1,'','','{\"limit\":50,\"orderBy\":\"name\",\"sortOrder\":\"asc\",\"filters\":[]}','supplier');

INSERT INTO `ps_attribute_group` VALUES (5,0,'select',4);

INSERT INTO `ps_attribute_group_lang` VALUES (5,1,'Weight','Weight');

INSERT INTO `ps_attribute_group_shop` VALUES (5,1);

INSERT INTO `ps_category` VALUES (10,2,1,2,17,20,1,'2025-10-09 13:38:36','2025-10-09 13:38:36',3,0);

INSERT INTO `ps_category` VALUES (11,10,1,3,18,19,1,'2025-10-09 13:38:39','2025-10-09 13:38:39',0,0);

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

INSERT INTO `ps_configuration_kpi` VALUES (37,NULL,NULL,'AVG_CUSTOMER_AGE',NULL,'2025-10-09 13:38:27','2025-10-09 13:38:27');

INSERT INTO `ps_configuration_kpi` VALUES (38,NULL,NULL,'AVG_CUSTOMER_AGE_EXPIRE',NULL,'2025-10-09 13:38:27','2025-10-09 13:38:27');

INSERT INTO `ps_configuration_kpi` VALUES (39,NULL,NULL,'ORDERS_PER_CUSTOMER','0','2025-10-09 13:38:27','2025-10-09 13:38:27');

INSERT INTO `ps_configuration_kpi` VALUES (40,NULL,NULL,'ORDERS_PER_CUSTOMER_EXPIRE','1760096307','2025-10-09 13:38:27','2025-10-09 13:38:27');

INSERT INTO `ps_configuration_kpi` VALUES (41,NULL,NULL,'CUSTOMER_MAIN_GENDER',NULL,'2025-10-09 13:38:27','2025-10-09 13:38:27');

INSERT INTO `ps_configuration_kpi` VALUES (42,NULL,NULL,'CUSTOMER_MAIN_GENDER_EXPIRE',NULL,'2025-10-09 13:38:27','2025-10-09 13:38:27');

INSERT INTO `ps_configuration_kpi` VALUES (43,NULL,NULL,'NEWSLETTER_REGISTRATIONS','1','2025-10-09 13:38:27','2025-10-09 13:38:27');

INSERT INTO `ps_configuration_kpi` VALUES (44,NULL,NULL,'NEWSLETTER_REGISTRATIONS_EXPIRE','1760031507','2025-10-09 13:38:27','2025-10-09 13:38:27');

INSERT INTO `ps_configuration_kpi` VALUES (45,NULL,NULL,'DISABLED_CATEGORIES','0','2025-10-09 13:38:37','2025-10-09 13:38:37');

INSERT INTO `ps_configuration_kpi` VALUES (46,NULL,NULL,'DISABLED_CATEGORIES_EXPIRE','1760017119','2025-10-09 13:38:37','2025-10-09 13:38:39');

INSERT INTO `ps_configuration_kpi` VALUES (47,NULL,NULL,'PRODUCTS_PER_CATEGORY','2','2025-10-09 13:38:37','2025-10-09 13:38:37');

INSERT INTO `ps_configuration_kpi` VALUES (48,NULL,NULL,'PRODUCTS_PER_CATEGORY_EXPIRE','1760013519','2025-10-09 13:38:37','2025-10-09 13:38:39');

INSERT INTO `ps_configuration_kpi` VALUES (49,NULL,NULL,'EMPTY_CATEGORIES','2','2025-10-09 13:38:37','2025-10-09 13:38:39');

INSERT INTO `ps_configuration_kpi` VALUES (50,NULL,NULL,'EMPTY_CATEGORIES_EXPIRE','1760017119','2025-10-09 13:38:37','2025-10-09 13:38:39');

INSERT INTO `ps_configuration_kpi` VALUES (51,NULL,NULL,'TOP_CATEGORY',NULL,'2025-10-09 13:38:37','2025-10-09 13:38:37');

INSERT INTO `ps_configuration_kpi` VALUES (52,NULL,NULL,'TOP_CATEGORY_EXPIRE',NULL,'2025-10-09 13:38:37','2025-10-09 13:38:37');

INSERT INTO `ps_configuration_kpi_lang` VALUES (37,1,'39 years','2025-10-09 13:38:27');

INSERT INTO `ps_configuration_kpi_lang` VALUES (38,1,'1760096307','2025-10-09 13:38:27');

INSERT INTO `ps_configuration_kpi_lang` VALUES (41,1,'100% Male Customers','2025-10-09 13:38:27');

INSERT INTO `ps_configuration_kpi_lang` VALUES (42,1,'1760096307','2025-10-09 13:38:27');

INSERT INTO `ps_configuration_kpi_lang` VALUES (51,1,'Art','2025-10-09 11:38:39');

INSERT INTO `ps_configuration_kpi_lang` VALUES (52,1,'1760096319','2025-10-09 11:38:39');

INSERT INTO `ps_customer` VALUES (3,1,1,1,3,1,0,NULL,NULL,NULL,'Jones','Jonathan','test@test.com','$2y$10$rgMONF0XwMiNnS0XfcqcK.mjMaNsVZN78tSWvod/G3KEZWgdu0L2e','2025-10-09 07:38:26','2003-01-01',0,NULL,'0000-00-00 00:00:00',0,NULL,0.000000,0,0,'8ca47a083192bc7200303730e5734862',NULL,1,0,0,'2025-10-09 13:38:26','2025-10-09 13:38:26',NULL,'0000-00-00 00:00:00');

INSERT INTO `ps_customer_group` VALUES (3,1);

INSERT INTO `ps_customer_group` VALUES (3,2);

INSERT INTO `ps_customer_group` VALUES (3,3);

INSERT INTO `ps_employee_session` VALUES (1,1,'189c40e11c72c5143d0fadef7c942d1f897105f8','2025-10-09 13:38:21','2025-10-09 13:38:49');

INSERT INTO `ps_feature` VALUES (3,2);

INSERT INTO `ps_feature_lang` VALUES (3,1,'Season');

INSERT INTO `ps_feature_shop` VALUES (3,1);

INSERT INTO `ps_layered_indexable_attribute_group` VALUES (5,0);

INSERT INTO `ps_layered_indexable_feature` VALUES (3,0);

INSERT INTO `ps_layered_indexable_feature_lang_value` VALUES (3,1,'','');

INSERT INTO `ps_layered_price_index` VALUES (20,1,1,9.000000,9.000000,8);

INSERT INTO `ps_layered_price_index` VALUES (20,1,1,9.000000,9.000000,17);

INSERT INTO `ps_layered_price_index` VALUES (20,1,1,9.000000,9.000000,21);

INSERT INTO `ps_layered_price_index` VALUES (20,2,1,10.466514,10.466514,8);

INSERT INTO `ps_layered_price_index` VALUES (20,2,1,10.466514,10.466514,17);

INSERT INTO `ps_layered_price_index` VALUES (20,2,1,10.466514,10.466514,21);

INSERT INTO `ps_log` VALUES (246,1,0,'Back office connection from 192.168.147.1','',0,NULL,NULL,1,1,1,'2025-10-09 13:38:21','2025-10-09 13:38:21');

INSERT INTO `ps_log` VALUES (247,1,0,'AttributeGroup addition','AttributeGroup',5,1,NULL,1,0,1,'2025-10-09 13:38:29','2025-10-09 13:38:29');

INSERT INTO `ps_log` VALUES (248,1,0,'Feature addition','Feature',3,1,NULL,1,0,1,'2025-10-09 13:38:31','2025-10-09 13:38:31');

INSERT INTO `ps_manufacturer` VALUES (3,'Nike','2025-10-09 13:38:34','2025-10-09 13:38:34',1);

INSERT INTO `ps_manufacturer_lang` VALUES (3,1,'<p>Description</p>','','','','');

INSERT INTO `ps_manufacturer_shop` VALUES (3,1);

INSERT INTO `ps_product` VALUES (20,2,2,2,1,0,0,0,'','','','',0.000000,0,1,0,0,9.000000,5.490000,'',0.000000,0.000000,0.000000,'test1','test1','',0.000000,0.000000,0.000000,0.000000,2,1,0,0,0,0,0,'default',0,1,'0000-00-00',0,'new',1,0,'both',0,0,1,0,'2025-10-09 13:38:42','2025-10-09 13:38:46',0,3,1,'virtual');

INSERT INTO `ps_product_lang` VALUES (20,1,1,'<p>Description</p>','<p>Vector graphic, format: svg. Download for personal, private and non-commercial use.</p>','bird-vector-graphics','','','','bird','','','','');

INSERT INTO `ps_product_shop` VALUES (20,1,2,0,0,0,0.000000,1,0,0,9.000000,5.490000,'',0.000000,0.000000,0.000000,0,0,0,0,'default',0,1,'0000-00-00',0,'new',1,0,'both',0,0,'2025-10-09 13:38:42','2025-10-09 13:38:46',3);

INSERT INTO `ps_product_supplier` VALUES (74,20,0,2,'test1',5.490000,1);

INSERT INTO `ps_product_supplier` VALUES (75,20,0,1,'test1',6.490000,1);

INSERT INTO `ps_stock_available` VALUES (59,20,0,1,0,300,300,0,0,1,'');

INSERT INTO `ps_stock_mvt` VALUES (1,59,NULL,NULL,11,1,'Doe','John',300,'2025-10-09 13:38:46',1,0.000000,0.000000,0.000000,NULL);

INSERT INTO `ps_supplier` VALUES (3,'Shoes supplier','2025-10-09 13:38:49','2025-10-09 13:38:49',1);

INSERT INTO `ps_supplier_lang` VALUES (3,1,'','','','');

INSERT INTO `ps_supplier_shop` VALUES (3,1);

-- Dump completed on 2025-10-09 11:38:50

