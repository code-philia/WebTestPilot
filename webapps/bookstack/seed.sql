
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
INSERT INTO `activities` VALUES (1,'auth_login','standard; (1) Admin',1,'192.168.117.1',NULL,NULL,'2025-10-08 17:50:59','2025-10-08 17:50:59');

INSERT INTO `activities` VALUES (2,'book_create','(1) Book1',1,'192.168.117.1',1,'book','2025-10-08 17:51:01','2025-10-08 17:51:01');

INSERT INTO `activities` VALUES (3,'book_create','(2) Book2',1,'192.168.117.1',2,'book','2025-10-08 17:51:03','2025-10-08 17:51:03');

INSERT INTO `activities` VALUES (4,'book_create','(3) Book',1,'192.168.117.1',3,'book','2025-10-08 17:51:04','2025-10-08 17:51:04');

INSERT INTO `activities` VALUES (5,'chapter_create','(1) Chapter',1,'192.168.117.1',1,'chapter','2025-10-08 17:51:06','2025-10-08 17:51:06');

INSERT INTO `activities` VALUES (6,'chapter_create','(2) Chapter 2',1,'192.168.117.1',2,'chapter','2025-10-08 17:51:09','2025-10-08 17:51:09');

INSERT INTO `activities` VALUES (7,'chapter_create','(3) Chapter 1',1,'192.168.117.1',3,'chapter','2025-10-08 17:51:12','2025-10-08 17:51:12');

INSERT INTO `activities` VALUES (8,'chapter_create','(4) Chapter 2',1,'192.168.117.1',4,'chapter','2025-10-08 17:51:14','2025-10-08 17:51:14');

INSERT INTO `activities` VALUES (9,'chapter_create','(5) Chapter',1,'192.168.117.1',5,'chapter','2025-10-08 17:51:16','2025-10-08 17:51:16');

INSERT INTO `activities` VALUES (10,'page_create','(1) Page 1',1,'192.168.117.1',1,'page','2025-10-08 17:51:19','2025-10-08 17:51:19');

INSERT INTO `activities` VALUES (11,'page_create','(2) Page 2',1,'192.168.117.1',2,'page','2025-10-08 17:51:23','2025-10-08 17:51:23');

INSERT INTO `activities` VALUES (12,'page_create','(3) Page',1,'192.168.117.1',3,'page','2025-10-08 17:51:25','2025-10-08 17:51:25');

INSERT INTO `activities` VALUES (13,'page_create','(4) Page 1',1,'192.168.117.1',4,'page','2025-10-08 17:51:27','2025-10-08 17:51:27');

INSERT INTO `activities` VALUES (14,'page_create','(5) Page Template',1,'192.168.117.1',5,'page','2025-10-08 17:51:29','2025-10-08 17:51:29');

INSERT INTO `activities` VALUES (15,'page_create','(6) Page',1,'192.168.117.1',6,'page','2025-10-08 17:51:32','2025-10-08 17:51:32');

INSERT INTO `activities` VALUES (16,'book_create','(4) Book1',1,'192.168.117.1',4,'book','2025-10-08 17:51:35','2025-10-08 17:51:35');

INSERT INTO `activities` VALUES (17,'book_create','(5) Book2',1,'192.168.117.1',5,'book','2025-10-08 17:51:37','2025-10-08 17:51:37');

INSERT INTO `activities` VALUES (18,'bookshelf_create','(1) Shelf',1,'192.168.117.1',1,'bookshelf','2025-10-08 17:51:38','2025-10-08 17:51:38');

INSERT INTO `activities` VALUES (19,'sort_rule_create','(1) Rule',1,'192.168.117.1',NULL,NULL,'2025-10-08 17:51:40','2025-10-08 17:51:40');

INSERT INTO `activities` VALUES (20,'role_create','(5) Role',1,'192.168.117.1',NULL,NULL,'2025-10-08 17:51:41','2025-10-08 17:51:41');

INSERT INTO `books` VALUES (1,'Book1','book1','Description','2025-10-08 17:51:01','2025-10-08 17:51:01',1,1,NULL,NULL,1,NULL,'<p>Description</p>',NULL);

INSERT INTO `books` VALUES (2,'Book2','book2','Description','2025-10-08 17:51:03','2025-10-08 17:51:03',1,1,NULL,NULL,1,NULL,'<p>Description</p>',NULL);

INSERT INTO `books` VALUES (3,'Book','book','Description','2025-10-08 17:51:04','2025-10-08 17:51:04',1,1,NULL,NULL,1,NULL,'<p>Description</p>',NULL);

INSERT INTO `books` VALUES (4,'Book1','book1-KaH','Description','2025-10-08 17:51:35','2025-10-08 17:51:35',1,1,NULL,NULL,1,NULL,'<p>Description</p>',NULL);

INSERT INTO `books` VALUES (5,'Book2','book2-wei','Description','2025-10-08 17:51:37','2025-10-08 17:51:37',1,1,NULL,NULL,1,NULL,'<p>Description</p>',NULL);

INSERT INTO `bookshelves` VALUES (1,'Shelf','shelf','Shelf Description',1,1,NULL,'2025-10-08 17:51:38','2025-10-08 17:51:38',NULL,1,'<p>Shelf Description</p>');

INSERT INTO `bookshelves_books` VALUES (1,1,0);

INSERT INTO `bookshelves_books` VALUES (1,2,1);

INSERT INTO `chapters` VALUES (1,3,'chapter','Chapter','Description',2,'2025-10-08 17:51:06','2025-10-08 17:51:06',1,1,NULL,1,'<p>Description</p>',NULL);

INSERT INTO `chapters` VALUES (2,1,'chapter-2','Chapter 2','Description',2,'2025-10-08 17:51:09','2025-10-08 17:51:09',1,1,NULL,1,'<p>Description</p>',NULL);

INSERT INTO `chapters` VALUES (3,2,'chapter-1','Chapter 1','Description',2,'2025-10-08 17:51:11','2025-10-08 17:51:11',1,1,NULL,1,'<p>Description</p>',NULL);

INSERT INTO `chapters` VALUES (4,2,'chapter-2','Chapter 2','Description',3,'2025-10-08 17:51:14','2025-10-08 17:51:14',1,1,NULL,1,'<p>Description</p>',NULL);

INSERT INTO `chapters` VALUES (5,2,'chapter','Chapter','Description',4,'2025-10-08 17:51:16','2025-10-08 17:51:16',1,1,NULL,1,'<p>Description</p>',NULL);

INSERT INTO `joint_permissions` VALUES (1,'book',1,3,1);

INSERT INTO `joint_permissions` VALUES (1,'book',2,3,1);

INSERT INTO `joint_permissions` VALUES (1,'book',3,3,1);

INSERT INTO `joint_permissions` VALUES (1,'book',4,3,1);

INSERT INTO `joint_permissions` VALUES (1,'book',5,3,1);

INSERT INTO `joint_permissions` VALUES (1,'bookshelf',1,3,1);

INSERT INTO `joint_permissions` VALUES (1,'chapter',1,3,1);

INSERT INTO `joint_permissions` VALUES (1,'chapter',2,3,1);

INSERT INTO `joint_permissions` VALUES (1,'chapter',3,3,1);

INSERT INTO `joint_permissions` VALUES (1,'chapter',4,3,1);

INSERT INTO `joint_permissions` VALUES (1,'chapter',5,3,1);

INSERT INTO `joint_permissions` VALUES (1,'page',1,3,1);

INSERT INTO `joint_permissions` VALUES (1,'page',2,3,1);

INSERT INTO `joint_permissions` VALUES (1,'page',3,3,1);

INSERT INTO `joint_permissions` VALUES (1,'page',4,3,1);

INSERT INTO `joint_permissions` VALUES (1,'page',5,3,1);

INSERT INTO `joint_permissions` VALUES (1,'page',6,3,1);

INSERT INTO `joint_permissions` VALUES (2,'book',1,1,1);

INSERT INTO `joint_permissions` VALUES (2,'book',2,1,1);

INSERT INTO `joint_permissions` VALUES (2,'book',3,1,1);

INSERT INTO `joint_permissions` VALUES (2,'book',4,1,1);

INSERT INTO `joint_permissions` VALUES (2,'book',5,1,1);

INSERT INTO `joint_permissions` VALUES (2,'bookshelf',1,1,1);

INSERT INTO `joint_permissions` VALUES (2,'chapter',1,1,1);

INSERT INTO `joint_permissions` VALUES (2,'chapter',2,1,1);

INSERT INTO `joint_permissions` VALUES (2,'chapter',3,1,1);

INSERT INTO `joint_permissions` VALUES (2,'chapter',4,1,1);

INSERT INTO `joint_permissions` VALUES (2,'chapter',5,1,1);

INSERT INTO `joint_permissions` VALUES (2,'page',1,1,1);

INSERT INTO `joint_permissions` VALUES (2,'page',2,1,1);

INSERT INTO `joint_permissions` VALUES (2,'page',3,1,1);

INSERT INTO `joint_permissions` VALUES (2,'page',4,1,1);

INSERT INTO `joint_permissions` VALUES (2,'page',5,1,1);

INSERT INTO `joint_permissions` VALUES (2,'page',6,1,1);

INSERT INTO `joint_permissions` VALUES (3,'book',1,1,1);

INSERT INTO `joint_permissions` VALUES (3,'book',2,1,1);

INSERT INTO `joint_permissions` VALUES (3,'book',3,1,1);

INSERT INTO `joint_permissions` VALUES (3,'book',4,1,1);

INSERT INTO `joint_permissions` VALUES (3,'book',5,1,1);

INSERT INTO `joint_permissions` VALUES (3,'bookshelf',1,1,1);

INSERT INTO `joint_permissions` VALUES (3,'chapter',1,1,1);

INSERT INTO `joint_permissions` VALUES (3,'chapter',2,1,1);

INSERT INTO `joint_permissions` VALUES (3,'chapter',3,1,1);

INSERT INTO `joint_permissions` VALUES (3,'chapter',4,1,1);

INSERT INTO `joint_permissions` VALUES (3,'chapter',5,1,1);

INSERT INTO `joint_permissions` VALUES (3,'page',1,1,1);

INSERT INTO `joint_permissions` VALUES (3,'page',2,1,1);

INSERT INTO `joint_permissions` VALUES (3,'page',3,1,1);

INSERT INTO `joint_permissions` VALUES (3,'page',4,1,1);

INSERT INTO `joint_permissions` VALUES (3,'page',5,1,1);

INSERT INTO `joint_permissions` VALUES (3,'page',6,1,1);

INSERT INTO `joint_permissions` VALUES (4,'book',1,1,1);

INSERT INTO `joint_permissions` VALUES (4,'book',2,1,1);

INSERT INTO `joint_permissions` VALUES (4,'book',3,1,1);

INSERT INTO `joint_permissions` VALUES (4,'book',4,1,1);

INSERT INTO `joint_permissions` VALUES (4,'book',5,1,1);

INSERT INTO `joint_permissions` VALUES (4,'bookshelf',1,1,1);

INSERT INTO `joint_permissions` VALUES (4,'chapter',1,1,1);

INSERT INTO `joint_permissions` VALUES (4,'chapter',2,1,1);

INSERT INTO `joint_permissions` VALUES (4,'chapter',3,1,1);

INSERT INTO `joint_permissions` VALUES (4,'chapter',4,1,1);

INSERT INTO `joint_permissions` VALUES (4,'chapter',5,1,1);

INSERT INTO `joint_permissions` VALUES (4,'page',1,1,1);

INSERT INTO `joint_permissions` VALUES (4,'page',2,1,1);

INSERT INTO `joint_permissions` VALUES (4,'page',3,1,1);

INSERT INTO `joint_permissions` VALUES (4,'page',4,1,1);

INSERT INTO `joint_permissions` VALUES (4,'page',5,1,1);

INSERT INTO `joint_permissions` VALUES (4,'page',6,1,1);

INSERT INTO `joint_permissions` VALUES (5,'book',1,1,1);

INSERT INTO `joint_permissions` VALUES (5,'book',2,1,1);

INSERT INTO `joint_permissions` VALUES (5,'book',3,1,1);

INSERT INTO `joint_permissions` VALUES (5,'book',4,1,1);

INSERT INTO `joint_permissions` VALUES (5,'book',5,1,1);

INSERT INTO `joint_permissions` VALUES (5,'bookshelf',1,1,1);

INSERT INTO `joint_permissions` VALUES (5,'chapter',1,1,1);

INSERT INTO `joint_permissions` VALUES (5,'chapter',2,1,1);

INSERT INTO `joint_permissions` VALUES (5,'chapter',3,1,1);

INSERT INTO `joint_permissions` VALUES (5,'chapter',4,1,1);

INSERT INTO `joint_permissions` VALUES (5,'chapter',5,1,1);

INSERT INTO `joint_permissions` VALUES (5,'page',1,1,1);

INSERT INTO `joint_permissions` VALUES (5,'page',2,1,1);

INSERT INTO `joint_permissions` VALUES (5,'page',3,1,1);

INSERT INTO `joint_permissions` VALUES (5,'page',4,1,1);

INSERT INTO `joint_permissions` VALUES (5,'page',5,1,1);

INSERT INTO `joint_permissions` VALUES (5,'page',6,1,1);

INSERT INTO `page_revisions` VALUES (1,1,'Page 1','<p id=\"bkmrk-page-description\">Page Description</p>','Page Description',1,'2025-10-08 17:51:19','2025-10-08 17:51:19','page-1','book1','version','','Initial publish',1);

INSERT INTO `page_revisions` VALUES (2,2,'Page 2','<p id=\"bkmrk-page-description\">Page Description</p>','Page Description',1,'2025-10-08 17:51:23','2025-10-08 17:51:23','page-2','book1','version','','Initial publish',1);

INSERT INTO `page_revisions` VALUES (3,3,'Page','<p id=\"bkmrk-page-description\">Page Description</p>','Page Description',1,'2025-10-08 17:51:25','2025-10-08 17:51:25','page','book1','version','','Initial publish',1);

INSERT INTO `page_revisions` VALUES (4,4,'Page 1','<p id=\"bkmrk-page-description\">Page Description</p>','Page Description',1,'2025-10-08 17:51:27','2025-10-08 17:51:27','page-1','book2','version','','Initial publish',1);

INSERT INTO `page_revisions` VALUES (5,5,'Page Template','<p id=\"bkmrk-page-description-tem\">Page Description Template</p>','Page Description Template',1,'2025-10-08 17:51:29','2025-10-08 17:51:29','page-template','book','version','','Initial publish',1);

INSERT INTO `page_revisions` VALUES (6,6,'Page','<p id=\"bkmrk-page-description\">Page Description</p>','Page Description',1,'2025-10-08 17:51:32','2025-10-08 17:51:32','page','book','version','','Initial publish',1);

INSERT INTO `pages` VALUES (1,1,0,'Page 1','page-1','<p id=\"bkmrk-page-description\">Page Description</p>','Page Description',3,'2025-10-08 17:51:18','2025-10-08 17:51:19',1,1,0,'',1,0,NULL,1,'wysiwyg');

INSERT INTO `pages` VALUES (2,1,0,'Page 2','page-2','<p id=\"bkmrk-page-description\">Page Description</p>','Page Description',4,'2025-10-08 17:51:22','2025-10-08 17:51:23',1,1,0,'',1,0,NULL,1,'wysiwyg');

INSERT INTO `pages` VALUES (3,1,0,'Page','page','<p id=\"bkmrk-page-description\">Page Description</p>','Page Description',5,'2025-10-08 17:51:25','2025-10-08 17:51:25',1,1,0,'',1,0,NULL,1,'wysiwyg');

INSERT INTO `pages` VALUES (4,2,0,'Page 1','page-1','<p id=\"bkmrk-page-description\">Page Description</p>','Page Description',5,'2025-10-08 17:51:26','2025-10-08 17:51:27',1,1,0,'',1,0,NULL,1,'wysiwyg');

INSERT INTO `pages` VALUES (5,3,0,'Page Template','page-template','<p id=\"bkmrk-page-description-tem\">Page Description Template</p>','Page Description Template',3,'2025-10-08 17:51:28','2025-10-08 17:51:29',1,1,0,'',1,0,NULL,1,'wysiwyg');

INSERT INTO `pages` VALUES (6,3,0,'Page','page','<p id=\"bkmrk-page-description\">Page Description</p>','Page Description',4,'2025-10-08 17:51:31','2025-10-08 17:51:32',1,1,0,'',1,0,NULL,1,'wysiwyg');

INSERT INTO `permission_role` VALUES (22,5);

INSERT INTO `permission_role` VALUES (24,5);

INSERT INTO `permission_role` VALUES (26,5);

INSERT INTO `permission_role` VALUES (27,5);

INSERT INTO `permission_role` VALUES (28,5);

INSERT INTO `permission_role` VALUES (29,5);

INSERT INTO `permission_role` VALUES (30,5);

INSERT INTO `permission_role` VALUES (31,5);

INSERT INTO `permission_role` VALUES (32,5);

INSERT INTO `permission_role` VALUES (33,5);

INSERT INTO `permission_role` VALUES (34,5);

INSERT INTO `permission_role` VALUES (35,5);

INSERT INTO `permission_role` VALUES (36,5);

INSERT INTO `permission_role` VALUES (37,5);

INSERT INTO `permission_role` VALUES (38,5);

INSERT INTO `permission_role` VALUES (39,5);

INSERT INTO `permission_role` VALUES (40,5);

INSERT INTO `permission_role` VALUES (41,5);

INSERT INTO `permission_role` VALUES (48,5);

INSERT INTO `permission_role` VALUES (49,5);

INSERT INTO `permission_role` VALUES (50,5);

INSERT INTO `permission_role` VALUES (51,5);

INSERT INTO `permission_role` VALUES (52,5);

INSERT INTO `permission_role` VALUES (53,5);

INSERT INTO `permission_role` VALUES (66,5);

INSERT INTO `permission_role` VALUES (67,5);

INSERT INTO `permission_role` VALUES (68,5);

INSERT INTO `permission_role` VALUES (70,5);

INSERT INTO `permission_role` VALUES (71,5);

INSERT INTO `permission_role` VALUES (72,5);

INSERT INTO `permission_role` VALUES (73,5);

INSERT INTO `roles` VALUES (5,'Role','Role description','2025-10-08 17:51:41','2025-10-08 17:51:41','','',0);

INSERT INTO `search_terms` VALUES (1,'Book1','book',1,48);

INSERT INTO `search_terms` VALUES (2,'Description','book',1,1);

INSERT INTO `search_terms` VALUES (3,'env','book',1,3);

INSERT INTO `search_terms` VALUES (4,'test','book',1,5);

INSERT INTO `search_terms` VALUES (5,'Book2','book',2,48);

INSERT INTO `search_terms` VALUES (6,'Description','book',2,1);

INSERT INTO `search_terms` VALUES (7,'env','book',2,3);

INSERT INTO `search_terms` VALUES (8,'test','book',2,5);

INSERT INTO `search_terms` VALUES (9,'Book','book',3,48);

INSERT INTO `search_terms` VALUES (10,'Description','book',3,1);

INSERT INTO `search_terms` VALUES (11,'env','book',3,3);

INSERT INTO `search_terms` VALUES (12,'test','book',3,5);

INSERT INTO `search_terms` VALUES (13,'Chapter','chapter',1,48);

INSERT INTO `search_terms` VALUES (14,'Description','chapter',1,1);

INSERT INTO `search_terms` VALUES (15,'Sample','chapter',1,8);

INSERT INTO `search_terms` VALUES (16,'Tag','chapter',1,8);

INSERT INTO `search_terms` VALUES (17,'Chapter','chapter',2,48);

INSERT INTO `search_terms` VALUES (18,'2','chapter',2,48);

INSERT INTO `search_terms` VALUES (19,'Description','chapter',2,1);

INSERT INTO `search_terms` VALUES (20,'Sample','chapter',2,8);

INSERT INTO `search_terms` VALUES (21,'Tag','chapter',2,8);

INSERT INTO `search_terms` VALUES (22,'Chapter','chapter',3,48);

INSERT INTO `search_terms` VALUES (23,'1','chapter',3,48);

INSERT INTO `search_terms` VALUES (24,'Description','chapter',3,1);

INSERT INTO `search_terms` VALUES (25,'Sample','chapter',3,8);

INSERT INTO `search_terms` VALUES (26,'Tag','chapter',3,8);

INSERT INTO `search_terms` VALUES (27,'Chapter','chapter',4,48);

INSERT INTO `search_terms` VALUES (28,'2','chapter',4,48);

INSERT INTO `search_terms` VALUES (29,'Description','chapter',4,1);

INSERT INTO `search_terms` VALUES (30,'Sample','chapter',4,8);

INSERT INTO `search_terms` VALUES (31,'Tag','chapter',4,8);

INSERT INTO `search_terms` VALUES (32,'Chapter','chapter',5,48);

INSERT INTO `search_terms` VALUES (33,'Description','chapter',5,1);

INSERT INTO `search_terms` VALUES (34,'Sample','chapter',5,8);

INSERT INTO `search_terms` VALUES (35,'Tag','chapter',5,8);

INSERT INTO `search_terms` VALUES (36,'Page','page',1,41);

INSERT INTO `search_terms` VALUES (37,'1','page',1,40);

INSERT INTO `search_terms` VALUES (38,'Description','page',1,1);

INSERT INTO `search_terms` VALUES (39,'Page','page',2,41);

INSERT INTO `search_terms` VALUES (40,'2','page',2,40);

INSERT INTO `search_terms` VALUES (41,'Description','page',2,1);

INSERT INTO `search_terms` VALUES (42,'Page','page',3,41);

INSERT INTO `search_terms` VALUES (43,'Description','page',3,1);

INSERT INTO `search_terms` VALUES (44,'Page','page',4,41);

INSERT INTO `search_terms` VALUES (45,'1','page',4,40);

INSERT INTO `search_terms` VALUES (46,'Description','page',4,1);

INSERT INTO `search_terms` VALUES (47,'Page','page',5,41);

INSERT INTO `search_terms` VALUES (48,'Template','page',5,41);

INSERT INTO `search_terms` VALUES (49,'Description','page',5,1);

INSERT INTO `search_terms` VALUES (50,'Page','page',6,41);

INSERT INTO `search_terms` VALUES (51,'Description','page',6,1);

INSERT INTO `search_terms` VALUES (52,'Book1','book',4,48);

INSERT INTO `search_terms` VALUES (53,'Description','book',4,1);

INSERT INTO `search_terms` VALUES (54,'env','book',4,3);

INSERT INTO `search_terms` VALUES (55,'test','book',4,5);

INSERT INTO `search_terms` VALUES (56,'Book2','book',5,48);

INSERT INTO `search_terms` VALUES (57,'Description','book',5,1);

INSERT INTO `search_terms` VALUES (58,'env','book',5,3);

INSERT INTO `search_terms` VALUES (59,'test','book',5,5);

INSERT INTO `search_terms` VALUES (60,'Shelf','bookshelf',1,49);

INSERT INTO `search_terms` VALUES (61,'Description','bookshelf',1,1);

INSERT INTO `sort_rules` VALUES (1,'Rule','name_asc,created_date_asc','2025-10-08 17:51:40','2025-10-08 17:51:40');

INSERT INTO `tags` VALUES (1,1,'book','env','test',0,'2025-10-08 17:51:01','2025-10-08 17:51:01');

INSERT INTO `tags` VALUES (2,2,'book','env','test',0,'2025-10-08 17:51:03','2025-10-08 17:51:03');

INSERT INTO `tags` VALUES (3,3,'book','env','test',0,'2025-10-08 17:51:04','2025-10-08 17:51:04');

INSERT INTO `tags` VALUES (4,1,'chapter','Sample Tag','Sample Tag',0,'2025-10-08 17:51:06','2025-10-08 17:51:06');

INSERT INTO `tags` VALUES (5,2,'chapter','Sample Tag','Sample Tag',0,'2025-10-08 17:51:09','2025-10-08 17:51:09');

INSERT INTO `tags` VALUES (6,3,'chapter','Sample Tag','Sample Tag',0,'2025-10-08 17:51:12','2025-10-08 17:51:12');

INSERT INTO `tags` VALUES (7,4,'chapter','Sample Tag','Sample Tag',0,'2025-10-08 17:51:14','2025-10-08 17:51:14');

INSERT INTO `tags` VALUES (8,5,'chapter','Sample Tag','Sample Tag',0,'2025-10-08 17:51:16','2025-10-08 17:51:16');

INSERT INTO `tags` VALUES (9,4,'book','env','test',0,'2025-10-08 17:51:35','2025-10-08 17:51:35');

INSERT INTO `tags` VALUES (10,5,'book','env','test',0,'2025-10-08 17:51:37','2025-10-08 17:51:37');

INSERT INTO `views` VALUES (1,1,1,'book',5,'2025-10-08 17:51:01','2025-10-08 17:51:24');

INSERT INTO `views` VALUES (2,1,2,'book',5,'2025-10-08 17:51:03','2025-10-08 17:51:26');

INSERT INTO `views` VALUES (3,1,3,'book',4,'2025-10-08 17:51:04','2025-10-08 17:51:31');

INSERT INTO `views` VALUES (4,1,1,'chapter',1,'2025-10-08 17:51:07','2025-10-08 17:51:07');

INSERT INTO `views` VALUES (5,1,2,'chapter',1,'2025-10-08 17:51:09','2025-10-08 17:51:09');

INSERT INTO `views` VALUES (6,1,3,'chapter',1,'2025-10-08 17:51:12','2025-10-08 17:51:12');

INSERT INTO `views` VALUES (7,1,4,'chapter',1,'2025-10-08 17:51:14','2025-10-08 17:51:14');

INSERT INTO `views` VALUES (8,1,5,'chapter',1,'2025-10-08 17:51:17','2025-10-08 17:51:17');

INSERT INTO `views` VALUES (9,1,1,'page',1,'2025-10-08 17:51:19','2025-10-08 17:51:19');

INSERT INTO `views` VALUES (10,1,2,'page',1,'2025-10-08 17:51:23','2025-10-08 17:51:23');

INSERT INTO `views` VALUES (11,1,3,'page',1,'2025-10-08 17:51:25','2025-10-08 17:51:25');

INSERT INTO `views` VALUES (12,1,4,'page',1,'2025-10-08 17:51:27','2025-10-08 17:51:27');

INSERT INTO `views` VALUES (13,1,5,'page',1,'2025-10-08 17:51:30','2025-10-08 17:51:30');

INSERT INTO `views` VALUES (14,1,6,'page',1,'2025-10-08 17:51:32','2025-10-08 17:51:32');

INSERT INTO `views` VALUES (15,1,4,'book',1,'2025-10-08 17:51:35','2025-10-08 17:51:35');

INSERT INTO `views` VALUES (16,1,5,'book',1,'2025-10-08 17:51:37','2025-10-08 17:51:37');

INSERT INTO `views` VALUES (17,1,1,'bookshelf',1,'2025-10-08 17:51:38','2025-10-08 17:51:38');

-- Dump completed on 2025-10-08 17:51:44

