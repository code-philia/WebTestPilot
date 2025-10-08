
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
INSERT INTO `activities` VALUES (1,'auth_login','standard; (1) Admin',1,'192.168.117.1',NULL,NULL,'2025-10-08 15:45:45','2025-10-08 15:45:45');

INSERT INTO `activities` VALUES (2,'book_create','(1) Book1',1,'192.168.117.1',1,'book','2025-10-08 15:45:47','2025-10-08 15:45:47');

INSERT INTO `activities` VALUES (3,'book_create','(2) Book2',1,'192.168.117.1',2,'book','2025-10-08 15:45:49','2025-10-08 15:45:49');

INSERT INTO `activities` VALUES (4,'book_create','(3) Book',1,'192.168.117.1',3,'book','2025-10-08 15:45:50','2025-10-08 15:45:50');

INSERT INTO `activities` VALUES (5,'chapter_create','(1) Chapter 1',1,'192.168.117.1',1,'chapter','2025-10-08 15:45:52','2025-10-08 15:45:52');

INSERT INTO `activities` VALUES (6,'chapter_create','(2) Chapter 2',1,'192.168.117.1',2,'chapter','2025-10-08 15:45:54','2025-10-08 15:45:54');

INSERT INTO `activities` VALUES (7,'chapter_create','(3) Chapter',1,'192.168.117.1',3,'chapter','2025-10-08 15:45:56','2025-10-08 15:45:56');

INSERT INTO `activities` VALUES (8,'chapter_create','(4) Chapter',1,'192.168.117.1',4,'chapter','2025-10-08 15:45:58','2025-10-08 15:45:58');

INSERT INTO `books` VALUES (1,'Book1','book1','Description','2025-10-08 15:45:47','2025-10-08 15:45:47',1,1,NULL,NULL,1,NULL,'<p>Description</p>',NULL);

INSERT INTO `books` VALUES (2,'Book2','book2','Description','2025-10-08 15:45:49','2025-10-08 15:45:49',1,1,NULL,NULL,1,NULL,'<p>Description</p>',NULL);

INSERT INTO `books` VALUES (3,'Book','book','Description','2025-10-08 15:45:50','2025-10-08 15:45:50',1,1,NULL,NULL,1,NULL,'<p>Description</p>',NULL);

INSERT INTO `chapters` VALUES (1,1,'chapter-1','Chapter 1','Description',2,'2025-10-08 15:45:52','2025-10-08 15:45:52',1,1,NULL,1,'<p>Description</p>',NULL);

INSERT INTO `chapters` VALUES (2,1,'chapter-2','Chapter 2','Description',3,'2025-10-08 15:45:54','2025-10-08 15:45:54',1,1,NULL,1,'<p>Description</p>',NULL);

INSERT INTO `chapters` VALUES (3,2,'chapter','Chapter','Description',2,'2025-10-08 15:45:56','2025-10-08 15:45:56',1,1,NULL,1,'<p>Description</p>',NULL);

INSERT INTO `chapters` VALUES (4,2,'chapter-itb','Chapter','Description',3,'2025-10-08 15:45:58','2025-10-08 15:45:58',1,1,NULL,1,'<p>Description</p>',NULL);

INSERT INTO `joint_permissions` VALUES (1,'book',1,3,1);

INSERT INTO `joint_permissions` VALUES (1,'book',2,3,1);

INSERT INTO `joint_permissions` VALUES (1,'book',3,3,1);

INSERT INTO `joint_permissions` VALUES (1,'chapter',1,3,1);

INSERT INTO `joint_permissions` VALUES (1,'chapter',2,3,1);

INSERT INTO `joint_permissions` VALUES (1,'chapter',3,3,1);

INSERT INTO `joint_permissions` VALUES (1,'chapter',4,3,1);

INSERT INTO `joint_permissions` VALUES (2,'book',1,1,1);

INSERT INTO `joint_permissions` VALUES (2,'book',2,1,1);

INSERT INTO `joint_permissions` VALUES (2,'book',3,1,1);

INSERT INTO `joint_permissions` VALUES (2,'chapter',1,1,1);

INSERT INTO `joint_permissions` VALUES (2,'chapter',2,1,1);

INSERT INTO `joint_permissions` VALUES (2,'chapter',3,1,1);

INSERT INTO `joint_permissions` VALUES (2,'chapter',4,1,1);

INSERT INTO `joint_permissions` VALUES (3,'book',1,1,1);

INSERT INTO `joint_permissions` VALUES (3,'book',2,1,1);

INSERT INTO `joint_permissions` VALUES (3,'book',3,1,1);

INSERT INTO `joint_permissions` VALUES (3,'chapter',1,1,1);

INSERT INTO `joint_permissions` VALUES (3,'chapter',2,1,1);

INSERT INTO `joint_permissions` VALUES (3,'chapter',3,1,1);

INSERT INTO `joint_permissions` VALUES (3,'chapter',4,1,1);

INSERT INTO `joint_permissions` VALUES (4,'book',1,1,1);

INSERT INTO `joint_permissions` VALUES (4,'book',2,1,1);

INSERT INTO `joint_permissions` VALUES (4,'book',3,1,1);

INSERT INTO `joint_permissions` VALUES (4,'chapter',1,1,1);

INSERT INTO `joint_permissions` VALUES (4,'chapter',2,1,1);

INSERT INTO `joint_permissions` VALUES (4,'chapter',3,1,1);

INSERT INTO `joint_permissions` VALUES (4,'chapter',4,1,1);

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

INSERT INTO `search_terms` VALUES (14,'1','chapter',1,48);

INSERT INTO `search_terms` VALUES (15,'Description','chapter',1,1);

INSERT INTO `search_terms` VALUES (16,'Sample','chapter',1,8);

INSERT INTO `search_terms` VALUES (17,'Tag','chapter',1,8);

INSERT INTO `search_terms` VALUES (18,'Chapter','chapter',2,48);

INSERT INTO `search_terms` VALUES (19,'2','chapter',2,48);

INSERT INTO `search_terms` VALUES (20,'Description','chapter',2,1);

INSERT INTO `search_terms` VALUES (21,'Sample','chapter',2,8);

INSERT INTO `search_terms` VALUES (22,'Tag','chapter',2,8);

INSERT INTO `search_terms` VALUES (23,'Chapter','chapter',3,48);

INSERT INTO `search_terms` VALUES (24,'Description','chapter',3,1);

INSERT INTO `search_terms` VALUES (25,'Sample','chapter',3,8);

INSERT INTO `search_terms` VALUES (26,'Tag','chapter',3,8);

INSERT INTO `search_terms` VALUES (27,'Chapter','chapter',4,48);

INSERT INTO `search_terms` VALUES (28,'Description','chapter',4,1);

INSERT INTO `search_terms` VALUES (29,'Sample','chapter',4,8);

INSERT INTO `search_terms` VALUES (30,'Tag','chapter',4,8);

INSERT INTO `tags` VALUES (1,1,'book','env','test',0,'2025-10-08 15:45:47','2025-10-08 15:45:47');

INSERT INTO `tags` VALUES (2,2,'book','env','test',0,'2025-10-08 15:45:49','2025-10-08 15:45:49');

INSERT INTO `tags` VALUES (3,3,'book','env','test',0,'2025-10-08 15:45:50','2025-10-08 15:45:50');

INSERT INTO `tags` VALUES (4,1,'chapter','Sample Tag','Sample Tag',0,'2025-10-08 15:45:52','2025-10-08 15:45:52');

INSERT INTO `tags` VALUES (5,2,'chapter','Sample Tag','Sample Tag',0,'2025-10-08 15:45:54','2025-10-08 15:45:54');

INSERT INTO `tags` VALUES (6,3,'chapter','Sample Tag','Sample Tag',0,'2025-10-08 15:45:56','2025-10-08 15:45:56');

INSERT INTO `tags` VALUES (7,4,'chapter','Sample Tag','Sample Tag',0,'2025-10-08 15:45:58','2025-10-08 15:45:58');

INSERT INTO `views` VALUES (1,1,1,'book',3,'2025-10-08 15:45:47','2025-10-08 15:45:53');

INSERT INTO `views` VALUES (2,1,2,'book',3,'2025-10-08 15:45:49','2025-10-08 15:45:57');

INSERT INTO `views` VALUES (3,1,3,'book',1,'2025-10-08 15:45:50','2025-10-08 15:45:50');

INSERT INTO `views` VALUES (4,1,1,'chapter',1,'2025-10-08 15:45:52','2025-10-08 15:45:52');

INSERT INTO `views` VALUES (5,1,2,'chapter',1,'2025-10-08 15:45:54','2025-10-08 15:45:54');

INSERT INTO `views` VALUES (6,1,3,'chapter',1,'2025-10-08 15:45:56','2025-10-08 15:45:56');

INSERT INTO `views` VALUES (7,1,4,'chapter',1,'2025-10-08 15:45:59','2025-10-08 15:45:59');

-- Dump completed on 2025-10-08 15:46:30

