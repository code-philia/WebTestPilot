INSERT INTO `activities` VALUES (1,1,1,1,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'192.168.148.1',0,'','2025-10-07 16:11:36.532809','2025-10-07 16:11:36.532809',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL);

INSERT INTO `activities` VALUES (2,1,1,1,NULL,1,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,4,'192.168.148.1',0,'','2025-10-07 16:11:51.653829','2025-10-07 16:11:51.653829',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL);

INSERT INTO `activities` VALUES (3,1,1,1,NULL,1,NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,14,'192.168.148.1',0,'','2025-10-07 16:11:57.804005','2025-10-07 16:11:57.804005',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL);

INSERT INTO `activities` VALUES (4,1,1,1,NULL,1,NULL,NULL,NULL,2,NULL,NULL,NULL,NULL,4,'192.168.148.1',0,'','2025-10-07 16:11:58.278537','2025-10-07 16:11:58.278537',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL);

INSERT INTO `activities` VALUES (5,1,1,1,NULL,1,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,5,'192.168.148.1',0,'','2025-10-07 16:11:58.289235','2025-10-07 16:11:58.289235',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL);

INSERT INTO `activities` VALUES (6,1,1,1,1,1,NULL,NULL,1,NULL,NULL,NULL,NULL,NULL,138,'127.0.0.1',1,'','2025-10-07 16:12:05.306501','2025-10-07 16:12:05.306501',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);

INSERT INTO `activities` VALUES (7,1,1,NULL,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,34,'192.168.148.1',0,'','2025-10-07 16:12:07.869931','2025-10-07 16:12:07.869931',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL);

INSERT INTO `backups` VALUES (1,2,'','2025-10-07 16:11:51.669525','2025-10-07 16:11:52.250385',120000.0000,'UaVngnaCmlFgL9HQOA98egfXHEv9i758/IAu4AajH9U7O1aBPmvkHeIyakGcu7LGG1o7aXcqi/backups/2025_10_07_b909d7fd1308d418a302c98e55b1ffc4.html','debian_docker');

INSERT INTO `backups` VALUES (2,3,'','2025-10-07 16:11:57.812057','2025-10-07 16:11:58.265571',120000.0000,'UaVngnaCmlFgL9HQOA98egfXHEv9i758/IAu4AajH9U7O1aBPmvkHeIyakGcu7LGG1o7aXcqi/backups/2025_10_07_c42062baa05df613348161420d4aedaf.html','debian_docker');

INSERT INTO `backups` VALUES (3,4,'','2025-10-07 16:11:58.288253','2025-10-07 16:11:58.776193',120000.0000,'UaVngnaCmlFgL9HQOA98egfXHEv9i758/IAu4AajH9U7O1aBPmvkHeIyakGcu7LGG1o7aXcqi/backups/2025_10_07_c42062baa05df613348161420d4aedaf.html','debian_docker');

INSERT INTO `backups` VALUES (4,5,'','2025-10-07 16:11:58.298740','2025-10-07 16:11:58.779464',120000.0000,'UaVngnaCmlFgL9HQOA98egfXHEv9i758/IAu4AajH9U7O1aBPmvkHeIyakGcu7LGG1o7aXcqi/backups/2025_10_07_c42062baa05df613348161420d4aedaf.html','debian_docker');

INSERT INTO `client_contacts` VALUES (1,1,1,1,'first_name','last_name','0912345678',NULL,NULL,NULL,NULL,'email@example.com',NULL,NULL,1,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'',NULL,0,1,'v6OiTIBZKOXOXz1P4mwoVLDRnT1wB3LD',NULL,'2025-10-07 16:11:34.437062','2025-10-07 16:11:34.437062',NULL);

INSERT INTO `clients` VALUES (1,1,1,NULL,'company_name','website.com','','','IAu4AajH9U7O1aBPmvkHeIyakGcu7LGG1o7aXcqi',NULL,'0987654321',0.000000,120000.000000,0.000000,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,840,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'{\"entity\":\"App\\\\Models\\\\Client\",\"industry_id\":\"\",\"size_id\":\"\",\"currency_id\":\"1\"}',0,NULL,'vat_number','company_number','2025-10-07 16:11:34.422234','2025-10-07 16:12:04.253276',NULL,'company_id',0.000000,NULL,NULL,0,0,'',NULL,NULL);

INSERT INTO `company_ledgers` VALUES (1,1,1,1,5,120000.000000,120000.000000,'Invoice 123456 marked as sent.','',1,'invoices','2025-10-07 16:11:47.275495','2025-10-07 16:11:48.625535');

INSERT INTO `company_ledgers` VALUES (2,1,1,1,11,-120000.000000,0.000000,'ApplyPaymentInvoice','',1,'App\\Models\\Payment','2025-10-07 16:12:04.242740','2025-10-07 16:12:04.818902');

INSERT INTO `credit_invitations` VALUES (1,1,1,1,1,'TI27mSB7N9KBRqqTMex4W0Qf3rHrfbS3',NULL,NULL,'','',NULL,NULL,NULL,NULL,'2025-10-07 16:11:57.514557','2025-10-07 16:11:57.514557',NULL,NULL,NULL);

INSERT INTO `credits` VALUES (1,1,1,NULL,1,1,NULL,NULL,NULL,2,NULL,'123456',0.000000,1,NULL,'2025-10-07',NULL,NULL,0,'[{\"_id\":\"74b3249c-9ccf-44e7-9c3a-17c2528a4418\",\"quantity\":1,\"cost\":60000,\"product_key\":\"product_name1\",\"product_cost\":0,\"notes\":\"product_description\",\"discount\":0,\"is_amount_discount\":true,\"tax_name1\":\"\",\"tax_rate1\":0,\"tax_name2\":\"\",\"tax_rate2\":0,\"tax_name3\":\"\",\"tax_rate3\":0,\"sort_id\":\"0\",\"line_total\":60000,\"tax_amount\":0,\"gross_line_total\":60000,\"date\":\"\",\"custom_value1\":\"\",\"custom_value2\":\"\",\"custom_value3\":\"\",\"custom_value4\":\"\",\"type_id\":\"1\",\"tax_id\":\"1\",\"net_cost\":0,\"task_id\":\"\",\"expense_id\":\"\",\"unit_code\":\"C62\"},{\"_id\":\"387f842e-c2cb-4c6f-a622-d5b414c74ac1\",\"quantity\":1,\"cost\":60000,\"product_key\":\"product_name2\",\"product_cost\":0,\"notes\":\"product_description\",\"discount\":0,\"is_amount_discount\":true,\"tax_name1\":\"\",\"tax_rate1\":0,\"tax_name2\":\"\",\"tax_rate2\":0,\"tax_name3\":\"\",\"tax_rate3\":0,\"sort_id\":\"0\",\"line_total\":60000,\"tax_amount\":0,\"gross_line_total\":60000,\"date\":\"\",\"custom_value1\":\"\",\"custom_value2\":\"\",\"custom_value3\":\"\",\"custom_value4\":\"\",\"type_id\":\"1\",\"tax_id\":\"1\",\"net_cost\":0,\"task_id\":\"\",\"expense_id\":\"\",\"unit_code\":\"C62\"}]',NULL,'','',NULL,'',NULL,0.000000,NULL,0.000000,NULL,0.000000,0.000000,0,NULL,NULL,NULL,NULL,NULL,0.000000,0.000000,0.000000,0.000000,0,0,0,0,1.000000,120000.000000,0.000000,0.000000,NULL,NULL,'2025-10-07 16:11:57.494408','2025-10-07 16:11:57.549278',NULL,NULL,NULL,NULL,NULL,0.000000,NULL,NULL,NULL,NULL);

INSERT INTO `expenses` VALUES (1,'2025-10-07 16:12:07.411439','2025-10-07 16:12:07.419073',NULL,1,NULL,1,NULL,NULL,1,NULL,1,12,NULL,NULL,NULL,0,23234.000000,0.000000,1.000000,NULL,0.000000,NULL,0.000000,NULL,0.000000,'2025-10-07',NULL,NULL,NULL,NULL,0,0,NULL,NULL,NULL,NULL,NULL,'0001',NULL,0.000000,0.000000,0.000000,0,0,NULL);

INSERT INTO `invoice_invitations` VALUES (1,1,1,1,1,'V7mmL27PuXcbEVeLjKDmb8QCJRRYFfRy',NULL,'8d8ddd4feb9c8251dcf8dfcd81358b75@example.com','','',NULL,'2025-10-07 16:12:05',NULL,NULL,'2025-10-07 16:11:46.300116','2025-10-07 16:12:05.252533',NULL,NULL,NULL);

INSERT INTO `invoice_invitations` VALUES (2,1,1,1,2,'nPEnlJH2vJTI8NbHKHBbjJjNYSh15Fum',NULL,NULL,'','',NULL,NULL,NULL,NULL,'2025-10-07 16:11:52.681722','2025-10-07 16:11:52.681722',NULL,NULL,NULL);

INSERT INTO `invoices` VALUES (1,1,1,NULL,1,4,NULL,NULL,NULL,2,'123456',0.000000,1,NULL,'2025-10-07',NULL,NULL,0,'[{\"_id\":\"4c7cf2e0-d3b6-4b0f-82b7-41d08b39406a\",\"quantity\":1,\"cost\":60000,\"product_key\":\"product_name1\",\"product_cost\":0,\"notes\":\"product_description\",\"discount\":0,\"is_amount_discount\":true,\"tax_name1\":\"\",\"tax_rate1\":0,\"tax_name2\":\"\",\"tax_rate2\":0,\"tax_name3\":\"\",\"tax_rate3\":0,\"sort_id\":\"0\",\"line_total\":60000,\"tax_amount\":0,\"gross_line_total\":60000,\"date\":\"\",\"custom_value1\":\"\",\"custom_value2\":\"\",\"custom_value3\":\"\",\"custom_value4\":\"\",\"type_id\":\"1\",\"tax_id\":\"1\",\"net_cost\":0,\"task_id\":\"\",\"expense_id\":\"\",\"unit_code\":\"C62\"},{\"_id\":\"8cfcb878-e26e-4bf8-ae88-66c4158e61cc\",\"quantity\":1,\"cost\":60000,\"product_key\":\"product_name2\",\"product_cost\":0,\"notes\":\"product_description\",\"discount\":0,\"is_amount_discount\":true,\"tax_name1\":\"\",\"tax_rate1\":0,\"tax_name2\":\"\",\"tax_rate2\":0,\"tax_name3\":\"\",\"tax_rate3\":0,\"sort_id\":\"0\",\"line_total\":60000,\"tax_amount\":0,\"gross_line_total\":60000,\"date\":\"\",\"custom_value1\":\"\",\"custom_value2\":\"\",\"custom_value3\":\"\",\"custom_value4\":\"\",\"type_id\":\"1\",\"tax_id\":\"1\",\"net_cost\":0,\"task_id\":\"\",\"expense_id\":\"\",\"unit_code\":\"C62\"}]',NULL,'','',NULL,'',NULL,0.000000,NULL,0.000000,NULL,0.000000,0.000000,0,NULL,NULL,NULL,NULL,NULL,0.000000,0.000000,0.000000,0.000000,0,0,0,0,1.000000,120000.000000,0.000000,NULL,NULL,NULL,'2025-10-07 16:11:46.261688','2025-10-07 16:12:05.274117',NULL,NULL,NULL,NULL,NULL,0,120000.000000,NULL,0,0,NULL,'[]',NULL,0.000000,NULL);

INSERT INTO `invoices` VALUES (2,1,1,NULL,1,1,NULL,NULL,NULL,2,'123456_draft',0.000000,1,NULL,'2025-10-07',NULL,NULL,0,'[{\"_id\":\"e8acefb4-759c-4d53-874b-fda9b887b999\",\"quantity\":1,\"cost\":60000,\"product_key\":\"product_name1\",\"product_cost\":0,\"notes\":\"product_description\",\"discount\":0,\"is_amount_discount\":true,\"tax_name1\":\"\",\"tax_rate1\":0,\"tax_name2\":\"\",\"tax_rate2\":0,\"tax_name3\":\"\",\"tax_rate3\":0,\"sort_id\":\"0\",\"line_total\":60000,\"tax_amount\":0,\"gross_line_total\":60000,\"date\":\"\",\"custom_value1\":\"\",\"custom_value2\":\"\",\"custom_value3\":\"\",\"custom_value4\":\"\",\"type_id\":\"1\",\"tax_id\":\"1\",\"net_cost\":0,\"task_id\":\"\",\"expense_id\":\"\",\"unit_code\":\"C62\"},{\"_id\":\"29b3d3a2-7ecf-4e96-82b0-fbba7d62c308\",\"quantity\":1,\"cost\":60000,\"product_key\":\"product_name2\",\"product_cost\":0,\"notes\":\"product_description\",\"discount\":0,\"is_amount_discount\":true,\"tax_name1\":\"\",\"tax_rate1\":0,\"tax_name2\":\"\",\"tax_rate2\":0,\"tax_name3\":\"\",\"tax_rate3\":0,\"sort_id\":\"0\",\"line_total\":60000,\"tax_amount\":0,\"gross_line_total\":60000,\"date\":\"\",\"custom_value1\":\"\",\"custom_value2\":\"\",\"custom_value3\":\"\",\"custom_value4\":\"\",\"type_id\":\"1\",\"tax_id\":\"1\",\"net_cost\":0,\"task_id\":\"\",\"expense_id\":\"\",\"unit_code\":\"C62\"}]',NULL,'','',NULL,'',NULL,0.000000,NULL,0.000000,NULL,0.000000,0.000000,0,NULL,NULL,NULL,NULL,NULL,0.000000,0.000000,0.000000,0.000000,0,0,0,0,1.000000,120000.000000,0.000000,0.000000,NULL,NULL,'2025-10-07 16:11:52.657133','2025-10-07 16:11:52.721955',NULL,NULL,NULL,NULL,NULL,0,0.000000,NULL,0,0,NULL,'[]',NULL,0.000000,NULL);

INSERT INTO `paymentables` VALUES (1,1,1,120000.0000,0.0000,'invoices','2025-10-07 16:12:04','2025-10-07 16:12:04',NULL);

INSERT INTO `payments` VALUES (1,1,1,NULL,NULL,1,NULL,NULL,NULL,NULL,NULL,1,4,120000.000000,0.000000,120000.000000,'2025-10-07',NULL,NULL,'0001',NULL,'2025-10-07 16:12:04.198792','2025-10-07 16:12:04.267847',NULL,0,1,1.000000,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'59aae89939750e4a2421bc482d286c02e1e4d26215d7538e0bc4dbafc459c757',NULL,NULL,NULL);

INSERT INTO `products` VALUES (1,1,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'product_name','product_description',0.000000,60000.000000,200.000000,'',0.000000,'',0.000000,'',0.000000,NULL,'2025-10-07 16:11:37.365727','2025-10-07 16:11:37.373911',0,0,0,0,1000,NULL,1,NULL,NULL);

INSERT INTO `products` VALUES (2,1,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'product_name1','product_description',0.000000,60000.000000,200.000000,'',0.000000,'',0.000000,'',0.000000,NULL,'2025-10-07 16:11:39.377519','2025-10-07 16:11:57.753042',0,0,0,0,1000,NULL,1,NULL,NULL);

INSERT INTO `products` VALUES (3,1,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'product_name2','product_description',0.000000,60000.000000,200.000000,'',0.000000,'',0.000000,'',0.000000,NULL,'2025-10-07 16:11:41.261632','2025-10-07 16:11:57.757714',0,0,0,0,1000,NULL,1,NULL,NULL);

INSERT INTO `system_logs` VALUES (1,1,1,NULL,5,61,800,'\"New login detected for your account. 192.168.148.1\"','2025-10-07 16:11:33.591602','2025-10-07 16:11:33.591602',NULL);

-- Dump completed on 2025-10-07 16:12:11

