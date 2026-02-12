
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
INSERT INTO `activities` VALUES (1,'auth_login','standard; (1) Admin',1,'192.168.117.1',NULL,NULL,'YYYY-MM-DD 13:18:32','YYYY-MM-DD 13:18:32');

INSERT INTO `activities` VALUES (2,'book_create','(1) Book1',1,'192.168.117.1',1,'book','YYYY-MM-DD 13:18:34','YYYY-MM-DD 13:18:34');

INSERT INTO `activities` VALUES (3,'book_create','(2) Book2',1,'192.168.117.1',2,'book','YYYY-MM-DD 13:18:36','YYYY-MM-DD 13:18:36');

INSERT INTO `activities` VALUES (4,'book_create','(3) Book',1,'192.168.117.1',3,'book','YYYY-MM-DD 13:18:38','YYYY-MM-DD 13:18:38');

INSERT INTO `activities` VALUES (5,'chapter_create','(1) Chapter',1,'192.168.117.1',1,'chapter','YYYY-MM-DD 13:18:39','YYYY-MM-DD 13:18:39');

INSERT INTO `activities` VALUES (6,'chapter_create','(2) Chapter 2',1,'192.168.117.1',2,'chapter','YYYY-MM-DD 13:18:41','YYYY-MM-DD 13:18:41');

INSERT INTO `activities` VALUES (7,'chapter_create','(3) Chapter 1',1,'192.168.117.1',3,'chapter','YYYY-MM-DD 13:18:43','YYYY-MM-DD 13:18:43');

INSERT INTO `activities` VALUES (8,'chapter_create','(4) Chapter 2',1,'192.168.117.1',4,'chapter','YYYY-MM-DD 13:18:45','YYYY-MM-DD 13:18:45');

INSERT INTO `activities` VALUES (9,'page_create','(1) Page 1',1,'192.168.117.1',1,'page','YYYY-MM-DD 13:18:47','YYYY-MM-DD 13:18:47');

INSERT INTO `activities` VALUES (10,'page_create','(2) Page 2',1,'192.168.117.1',2,'page','YYYY-MM-DD 13:18:50','YYYY-MM-DD 13:18:50');

INSERT INTO `activities` VALUES (11,'page_create','(3) Page',1,'192.168.117.1',3,'page','YYYY-MM-DD 13:18:52','YYYY-MM-DD 13:18:52');

INSERT INTO `activities` VALUES (12,'page_create','(4) Page 1',1,'192.168.117.1',4,'page','YYYY-MM-DD 13:18:54','YYYY-MM-DD 13:18:54');

INSERT INTO `activities` VALUES (13,'page_create','(5) Page Template',1,'192.168.117.1',5,'page','YYYY-MM-DD 13:18:56','YYYY-MM-DD 13:18:56');

INSERT INTO `activities` VALUES (14,'page_create','(6) Page',1,'192.168.117.1',6,'page','YYYY-MM-DD 13:18:58','YYYY-MM-DD 13:18:58');

INSERT INTO `activities` VALUES (15,'bookshelf_create','(1) Shelf',1,'192.168.117.1',1,'bookshelf','YYYY-MM-DD 13:18:59','YYYY-MM-DD 13:18:59');

INSERT INTO `activities` VALUES (16,'sort_rule_create','(1) Rule',1,'192.168.117.1',NULL,NULL,'YYYY-MM-DD 13:19:01','YYYY-MM-DD 13:19:01');

INSERT INTO `activities` VALUES (17,'role_create','(5) Role',1,'192.168.117.1',NULL,NULL,'YYYY-MM-DD 13:19:02','YYYY-MM-DD 13:19:02');

INSERT INTO `activities` VALUES (18,'auth_login','standard; (1) Admin',1,'192.168.117.1',NULL,NULL,'YYYY-MM-DD 13:19:09','YYYY-MM-DD 13:19:09');

INSERT INTO `activities` VALUES (20,'comment_create','Comment #1 (ID: 1) for page (ID: 5)',1,'172.21.184.1',NULL,NULL,'YYYY-MM-DD 03:35:55','YYYY-MM-DD 03:35:55');

INSERT INTO `activities` VALUES (21,'commented_on','(5) Page Template',1,'172.21.184.1',5,'page','YYYY-MM-DD 03:35:55','YYYY-MM-DD 03:35:55');

INSERT INTO `activities` VALUES (22,'comment_create','Comment #2 (ID: 2) for page (ID: 5)',1,'172.21.184.1',NULL,NULL,'YYYY-MM-DD 03:36:01','YYYY-MM-DD 03:36:01');

INSERT INTO `activities` VALUES (23,'commented_on','(5) Page Template',1,'172.21.184.1',5,'page','YYYY-MM-DD 03:36:01','YYYY-MM-DD 03:36:01');

INSERT INTO `activities` VALUES (24,'comment_create','Comment #3 (ID: 3) for page (ID: 5)',1,'172.21.184.1',NULL,NULL,'YYYY-MM-DD 03:36:07','YYYY-MM-DD 03:36:07');

INSERT INTO `activities` VALUES (25,'commented_on','(5) Page Template',1,'172.21.184.1',5,'page','YYYY-MM-DD 03:36:07','YYYY-MM-DD 03:36:07');

INSERT INTO `activities` VALUES (26,'comment_create','Comment #4 (ID: 4) for page (ID: 5)',1,'172.21.184.1',NULL,NULL,'YYYY-MM-DD 03:36:13','YYYY-MM-DD 03:36:13');

INSERT INTO `activities` VALUES (27,'commented_on','(5) Page Template',1,'172.21.184.1',5,'page','YYYY-MM-DD 03:36:13','YYYY-MM-DD 03:36:13');

INSERT INTO `activities` VALUES (28,'comment_create','Comment #5 (ID: 5) for page (ID: 5)',1,'172.21.184.1',NULL,NULL,'YYYY-MM-DD 03:36:22','YYYY-MM-DD 03:36:22');

INSERT INTO `activities` VALUES (29,'commented_on','(5) Page Template',1,'172.21.184.1',5,'page','YYYY-MM-DD 03:36:22','YYYY-MM-DD 03:36:22');

INSERT INTO `books` VALUES (1,'Book1','book1','Description','YYYY-MM-DD 13:18:34','YYYY-MM-DD 13:18:34',1,1,NULL,NULL,1,NULL,'<p>Description</p>',NULL);

INSERT INTO `books` VALUES (2,'Book2','book2','Description','YYYY-MM-DD 13:18:36','YYYY-MM-DD 13:18:36',1,1,NULL,NULL,1,NULL,'<p>Description</p>',NULL);

INSERT INTO `books` VALUES (3,'Book','book','Description','YYYY-MM-DD 13:18:37','YYYY-MM-DD 13:18:37',1,1,NULL,NULL,1,NULL,'<p>Description</p>',NULL);

INSERT INTO `bookshelves` VALUES (1,'Shelf','shelf','Shelf Description',1,1,NULL,'YYYY-MM-DD 13:18:59','YYYY-MM-DD 13:18:59',NULL,1,'<p>Shelf Description</p>');

INSERT INTO `bookshelves_books` VALUES (1,1,0);

INSERT INTO `bookshelves_books` VALUES (1,2,1);

INSERT INTO `chapters` VALUES (1,3,'chapter','Chapter','Description',2,'YYYY-MM-DD 13:18:39','YYYY-MM-DD 13:18:39',1,1,NULL,1,'<p>Description</p>',NULL);

INSERT INTO `chapters` VALUES (2,1,'chapter-2','Chapter 2','Description',2,'YYYY-MM-DD 13:18:41','YYYY-MM-DD 13:18:41',1,1,NULL,1,'<p>Description</p>',NULL);

INSERT INTO `chapters` VALUES (3,2,'chapter-1','Chapter 1','Description',2,'YYYY-MM-DD 13:18:43','YYYY-MM-DD 13:18:43',1,1,NULL,1,'<p>Description</p>',NULL);

INSERT INTO `chapters` VALUES (4,2,'chapter-2','Chapter 2','Description',3,'YYYY-MM-DD 13:18:45','YYYY-MM-DD 13:18:45',1,1,NULL,1,'<p>Description</p>',NULL);

INSERT INTO `favourites` VALUES (1,1,1,'book','YYYY-MM-DD 13:19:04','YYYY-MM-DD 13:19:04');

INSERT INTO `favourites` VALUES (2,1,2,'chapter','YYYY-MM-DD 13:19:06','YYYY-MM-DD 13:19:06');

INSERT INTO `favourites` VALUES (3,1,1,'page','YYYY-MM-DD 13:19:08','YYYY-MM-DD 13:19:08');

INSERT INTO `favourites` VALUES (4,1,1,'bookshelf','YYYY-MM-DD 13:19:10','YYYY-MM-DD 13:19:10');

INSERT INTO `joint_permissions` VALUES (1,'book',1,3,1);

INSERT INTO `joint_permissions` VALUES (1,'book',2,3,1);

INSERT INTO `joint_permissions` VALUES (1,'book',3,3,1);

INSERT INTO `joint_permissions` VALUES (1,'bookshelf',1,3,1);

INSERT INTO `joint_permissions` VALUES (1,'chapter',1,3,1);

INSERT INTO `joint_permissions` VALUES (1,'chapter',2,3,1);

INSERT INTO `joint_permissions` VALUES (1,'chapter',3,3,1);

INSERT INTO `joint_permissions` VALUES (1,'chapter',4,3,1);

INSERT INTO `joint_permissions` VALUES (1,'page',1,3,1);

INSERT INTO `joint_permissions` VALUES (1,'page',2,3,1);

INSERT INTO `joint_permissions` VALUES (1,'page',3,3,1);

INSERT INTO `joint_permissions` VALUES (1,'page',4,3,1);

INSERT INTO `joint_permissions` VALUES (1,'page',5,3,1);

INSERT INTO `joint_permissions` VALUES (1,'page',6,3,1);

INSERT INTO `joint_permissions` VALUES (2,'book',1,1,1);

INSERT INTO `joint_permissions` VALUES (2,'book',2,1,1);

INSERT INTO `joint_permissions` VALUES (2,'book',3,1,1);

INSERT INTO `joint_permissions` VALUES (2,'bookshelf',1,1,1);

INSERT INTO `joint_permissions` VALUES (2,'chapter',1,1,1);

INSERT INTO `joint_permissions` VALUES (2,'chapter',2,1,1);

INSERT INTO `joint_permissions` VALUES (2,'chapter',3,1,1);

INSERT INTO `joint_permissions` VALUES (2,'chapter',4,1,1);

INSERT INTO `joint_permissions` VALUES (2,'page',1,1,1);

INSERT INTO `joint_permissions` VALUES (2,'page',2,1,1);

INSERT INTO `joint_permissions` VALUES (2,'page',3,1,1);

INSERT INTO `joint_permissions` VALUES (2,'page',4,1,1);

INSERT INTO `joint_permissions` VALUES (2,'page',5,1,1);

INSERT INTO `joint_permissions` VALUES (2,'page',6,1,1);

INSERT INTO `joint_permissions` VALUES (3,'book',1,1,1);

INSERT INTO `joint_permissions` VALUES (3,'book',2,1,1);

INSERT INTO `joint_permissions` VALUES (3,'book',3,1,1);

INSERT INTO `joint_permissions` VALUES (3,'bookshelf',1,1,1);

INSERT INTO `joint_permissions` VALUES (3,'chapter',1,1,1);

INSERT INTO `joint_permissions` VALUES (3,'chapter',2,1,1);

INSERT INTO `joint_permissions` VALUES (3,'chapter',3,1,1);

INSERT INTO `joint_permissions` VALUES (3,'chapter',4,1,1);

INSERT INTO `joint_permissions` VALUES (3,'page',1,1,1);

INSERT INTO `joint_permissions` VALUES (3,'page',2,1,1);

INSERT INTO `joint_permissions` VALUES (3,'page',3,1,1);

INSERT INTO `joint_permissions` VALUES (3,'page',4,1,1);

INSERT INTO `joint_permissions` VALUES (3,'page',5,1,1);

INSERT INTO `joint_permissions` VALUES (3,'page',6,1,1);

INSERT INTO `joint_permissions` VALUES (4,'book',1,1,1);

INSERT INTO `joint_permissions` VALUES (4,'book',2,1,1);

INSERT INTO `joint_permissions` VALUES (4,'book',3,1,1);

INSERT INTO `joint_permissions` VALUES (4,'bookshelf',1,1,1);

INSERT INTO `joint_permissions` VALUES (4,'chapter',1,1,1);

INSERT INTO `joint_permissions` VALUES (4,'chapter',2,1,1);

INSERT INTO `joint_permissions` VALUES (4,'chapter',3,1,1);

INSERT INTO `joint_permissions` VALUES (4,'chapter',4,1,1);

INSERT INTO `joint_permissions` VALUES (4,'page',1,1,1);

INSERT INTO `joint_permissions` VALUES (4,'page',2,1,1);

INSERT INTO `joint_permissions` VALUES (4,'page',3,1,1);

INSERT INTO `joint_permissions` VALUES (4,'page',4,1,1);

INSERT INTO `joint_permissions` VALUES (4,'page',5,1,1);

INSERT INTO `joint_permissions` VALUES (4,'page',6,1,1);

INSERT INTO `joint_permissions` VALUES (5,'book',1,1,1);

INSERT INTO `joint_permissions` VALUES (5,'book',2,1,1);

INSERT INTO `joint_permissions` VALUES (5,'book',3,1,1);

INSERT INTO `joint_permissions` VALUES (5,'bookshelf',1,1,1);

INSERT INTO `joint_permissions` VALUES (5,'chapter',1,1,1);

INSERT INTO `joint_permissions` VALUES (5,'chapter',2,1,1);

INSERT INTO `joint_permissions` VALUES (5,'chapter',3,1,1);

INSERT INTO `joint_permissions` VALUES (5,'chapter',4,1,1);

INSERT INTO `joint_permissions` VALUES (5,'page',1,1,1);

INSERT INTO `joint_permissions` VALUES (5,'page',2,1,1);

INSERT INTO `joint_permissions` VALUES (5,'page',3,1,1);

INSERT INTO `joint_permissions` VALUES (5,'page',4,1,1);

INSERT INTO `joint_permissions` VALUES (5,'page',5,1,1);

INSERT INTO `joint_permissions` VALUES (5,'page',6,1,1);

INSERT INTO `page_revisions` VALUES (1,1,'Page 1','<p id=\"bkmrk-page-description\">Page Description</p>','Page Description',1,'YYYY-MM-DD 13:18:47','YYYY-MM-DD 13:18:47','page-1','book1','version','','Initial publish',1);

INSERT INTO `page_revisions` VALUES (2,2,'Page 2','<p id=\"bkmrk-page-description\">Page Description</p>','Page Description',1,'YYYY-MM-DD 13:18:50','YYYY-MM-DD 13:18:50','page-2','book1','version','','Initial publish',1);

INSERT INTO `page_revisions` VALUES (3,3,'Page','<p id=\"bkmrk-page-description\">Page Description</p>','Page Description',1,'YYYY-MM-DD 13:18:51','YYYY-MM-DD 13:18:52','page','book1','version','','Initial publish',1);

INSERT INTO `page_revisions` VALUES (4,4,'Page 1','<p id=\"bkmrk-page-description\">Page Description</p>','Page Description',1,'YYYY-MM-DD 13:18:53','YYYY-MM-DD 13:18:53','page-1','book2','version','','Initial publish',1);

INSERT INTO `page_revisions` VALUES (5,5,'Page Template','<p id=\"bkmrk-page-description-tem\">Page Description Template</p>','Page Description Template',1,'YYYY-MM-DD 13:18:56','YYYY-MM-DD 13:18:56','page-template','book','version','','Initial publish',1);

INSERT INTO `page_revisions` VALUES (6,6,'Page','<p id=\"bkmrk-page-description\">Page Description</p>','Page Description',1,'YYYY-MM-DD 13:18:58','YYYY-MM-DD 13:18:58','page','book','version','','Initial publish',1);

INSERT INTO `pages` VALUES (1,1,0,'Page 1','page-1','<p id=\"bkmrk-page-description\">Page Description</p>','Page Description',3,'YYYY-MM-DD 13:18:46','YYYY-MM-DD 13:18:47',1,1,0,'',1,0,NULL,1,'wysiwyg');

INSERT INTO `pages` VALUES (2,1,0,'Page 2','page-2','<p id=\"bkmrk-page-description\">Page Description</p>','Page Description',4,'YYYY-MM-DD 13:18:49','YYYY-MM-DD 13:18:50',1,1,0,'',1,0,NULL,1,'wysiwyg');

INSERT INTO `pages` VALUES (3,1,0,'Page','page','<p id=\"bkmrk-page-description\">Page Description</p>','Page Description',5,'YYYY-MM-DD 13:18:51','YYYY-MM-DD 13:18:51',1,1,0,'',1,0,NULL,1,'wysiwyg');

INSERT INTO `pages` VALUES (4,2,0,'Page 1','page-1','<p id=\"bkmrk-page-description\">Page Description</p>','Page Description',4,'YYYY-MM-DD 13:18:53','YYYY-MM-DD 13:18:53',1,1,0,'',1,0,NULL,1,'wysiwyg');

INSERT INTO `pages` VALUES (5,3,0,'Page Template','page-template','<p id=\"bkmrk-page-description-tem\">Page Description Template</p>','Page Description Template',3,'YYYY-MM-DD 13:18:55','YYYY-MM-DD 13:18:56',1,1,0,'',1,0,NULL,1,'wysiwyg');

INSERT INTO `pages` VALUES (6,3,0,'Page','page','<p id=\"bkmrk-page-description\">Page Description</p>','Page Description',4,'YYYY-MM-DD 13:18:57','YYYY-MM-DD 13:18:58',1,1,0,'',1,0,NULL,1,'wysiwyg');

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

INSERT INTO `roles` VALUES (5,'Role','Role description','YYYY-MM-DD 13:19:02','YYYY-MM-DD 13:19:02','','',0);

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

INSERT INTO `search_terms` VALUES (32,'Page','page',1,41);

INSERT INTO `search_terms` VALUES (33,'1','page',1,40);

INSERT INTO `search_terms` VALUES (34,'Description','page',1,1);

INSERT INTO `search_terms` VALUES (35,'Page','page',2,41);

INSERT INTO `search_terms` VALUES (36,'2','page',2,40);

INSERT INTO `search_terms` VALUES (37,'Description','page',2,1);

INSERT INTO `search_terms` VALUES (38,'Page','page',3,41);

INSERT INTO `search_terms` VALUES (39,'Description','page',3,1);

INSERT INTO `search_terms` VALUES (40,'Page','page',4,41);

INSERT INTO `search_terms` VALUES (41,'1','page',4,40);

INSERT INTO `search_terms` VALUES (42,'Description','page',4,1);

INSERT INTO `search_terms` VALUES (43,'Page','page',5,41);

INSERT INTO `search_terms` VALUES (44,'Template','page',5,41);

INSERT INTO `search_terms` VALUES (45,'Description','page',5,1);

INSERT INTO `search_terms` VALUES (46,'Page','page',6,41);

INSERT INTO `search_terms` VALUES (47,'Description','page',6,1);

INSERT INTO `search_terms` VALUES (48,'Shelf','bookshelf',1,49);

INSERT INTO `search_terms` VALUES (49,'Description','bookshelf',1,1);

INSERT INTO `sort_rules` VALUES (1,'Rule','name_asc,created_date_asc','YYYY-MM-DD 13:19:00','YYYY-MM-DD 13:19:00');

INSERT INTO `tags` VALUES (1,1,'book','env','test',0,'YYYY-MM-DD 13:18:34','YYYY-MM-DD 13:18:34');

INSERT INTO `tags` VALUES (2,2,'book','env','test',0,'YYYY-MM-DD 13:18:36','YYYY-MM-DD 13:18:36');

INSERT INTO `tags` VALUES (3,3,'book','env','test',0,'YYYY-MM-DD 13:18:37','YYYY-MM-DD 13:18:37');

INSERT INTO `tags` VALUES (4,1,'chapter','Sample Tag','Sample Tag',0,'YYYY-MM-DD 13:18:39','YYYY-MM-DD 13:18:39');

INSERT INTO `tags` VALUES (5,2,'chapter','Sample Tag','Sample Tag',0,'YYYY-MM-DD 13:18:41','YYYY-MM-DD 13:18:41');

INSERT INTO `tags` VALUES (6,3,'chapter','Sample Tag','Sample Tag',0,'YYYY-MM-DD 13:18:43','YYYY-MM-DD 13:18:43');

INSERT INTO `tags` VALUES (7,4,'chapter','Sample Tag','Sample Tag',0,'YYYY-MM-DD 13:18:45','YYYY-MM-DD 13:18:45');

INSERT INTO `views` VALUES (1,1,1,'book',9,'YYYY-MM-DD 13:18:34','YYYY-MM-DD 13:19:07');

INSERT INTO `views` VALUES (2,1,2,'book',4,'YYYY-MM-DD 13:18:36','YYYY-MM-DD 13:18:52');

INSERT INTO `views` VALUES (3,1,3,'book',4,'YYYY-MM-DD 13:18:38','YYYY-MM-DD 13:18:57');

INSERT INTO `views` VALUES (4,1,1,'chapter',1,'YYYY-MM-DD 13:18:40','YYYY-MM-DD 13:18:40');

INSERT INTO `views` VALUES (5,1,2,'chapter',3,'YYYY-MM-DD 13:18:42','YYYY-MM-DD 13:19:06');

INSERT INTO `views` VALUES (6,1,3,'chapter',1,'YYYY-MM-DD 13:18:44','YYYY-MM-DD 13:18:44');

INSERT INTO `views` VALUES (7,1,4,'chapter',1,'YYYY-MM-DD 13:18:45','YYYY-MM-DD 13:18:45');

INSERT INTO `views` VALUES (8,1,1,'page',3,'YYYY-MM-DD 13:18:48','YYYY-MM-DD 13:19:08');

INSERT INTO `views` VALUES (9,1,2,'page',1,'YYYY-MM-DD 13:18:50','YYYY-MM-DD 13:18:50');

INSERT INTO `views` VALUES (10,1,3,'page',1,'YYYY-MM-DD 13:18:52','YYYY-MM-DD 13:18:52');

INSERT INTO `views` VALUES (11,1,4,'page',1,'YYYY-MM-DD 13:18:54','YYYY-MM-DD 13:18:54');

INSERT INTO `views` VALUES (12,1,5,'page',1,'YYYY-MM-DD 13:18:56','YYYY-MM-DD 13:18:56');

INSERT INTO `views` VALUES (13,1,6,'page',1,'YYYY-MM-DD 13:18:58','YYYY-MM-DD 13:18:58');

INSERT INTO `views` VALUES (14,1,1,'bookshelf',3,'YYYY-MM-DD 13:18:59','YYYY-MM-DD 13:19:11');

INSERT INTO `comments` VALUES (1,5,'page',NULL,'<p>Comment</p>',NULL,1,1,1,'YYYY-MM-DD 03:35:55','YYYY-MM-DD 03:35:55');

INSERT INTO `comments` VALUES (2,5,'page',NULL,'<p>Comment</p>',NULL,2,1,1,'YYYY-MM-DD 03:36:01','YYYY-MM-DD 03:36:01');

INSERT INTO `comments` VALUES (3,5,'page',NULL,'<p>Reply</p>',1,3,1,1,'YYYY-MM-DD 03:36:07','YYYY-MM-DD 03:36:07');

INSERT INTO `comments` VALUES (4,5,'page',NULL,'<p>Reply</p>',3,4,1,1,'YYYY-MM-DD 03:36:13','YYYY-MM-DD 03:36:13');

INSERT INTO `comments` VALUES (5,5,'page',NULL,'<p>Reply</p>',3,5,1,1,'YYYY-MM-DD 03:36:22','YYYY-MM-DD 03:36:22');

-- Dump completed on YYYY-MM-DD 13:19:11

