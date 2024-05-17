/*
 Navicat Premium Data Transfer

 Source Server         : 本地mysql
 Source Server Type    : MySQL
 Source Server Version : 80036
 Source Host           : localhost:3306
 Source Schema         : ipv6test

 Target Server Type    : MySQL
 Target Server Version : 80036
 File Encoding         : 65001

 Date: 17/04/2024 10:32:37
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for ipv6_support_degree
-- ----------------------------
DROP TABLE IF EXISTS `ipv6_support_degree`;
CREATE TABLE `ipv6_support_degree`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID，作为主键',
  `domain` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '网站域名',
  `resolved` tinyint NULL DEFAULT NULL COMMENT '是否可以被解析',
  `accessed` tinyint NULL DEFAULT NULL COMMENT '是否可以被访问',
  `support_degree` double NULL DEFAULT NULL COMMENT 'ipv6支持度，默认为百分比',
  `connectivity` double NULL DEFAULT NULL  COMMENT 'ipv6连通性',
  `secondary_connectivity` double NULL DEFAULT NULL COMMENT '二级链接连通性',
  `tertiary_connectivity` double NULL DEFAULT NULL  COMMENT '三级链接连通性',
  `resolve_delay` double NULL DEFAULT NULL COMMENT '域名解析时延指标',
  `TCP_establishment_resolution_delay` double NULL DEFAULT NULL COMMENT 'TCP建立解析时延指标',
  `server_responds_first_packet_delay` double NULL DEFAULT NULL COMMENT '服务器响应首包时延指标',
  `server_responds_first_page_delay` double NULL DEFAULT NULL COMMENT '服务器响应首页时延指标',
  `access_stability` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'ipv6访问稳定性',
  `ipv6_authorization_system` tinyint NULL DEFAULT NULL COMMENT '是否具备ipv6授权体系',
  `start_time` timestamp(6) NULL DEFAULT NULL COMMENT '计算开始时间',
  `end_time` timestamp(6) NULL DEFAULT NULL COMMENT '计算完成时间',
  `text_similarity` double NULL DEFAULT NULL COMMENT '文本相似度',
  `pic_similarity` double NULL DEFAULT NULL COMMENT '图片相似度',
  `text_structure_similarity` double NULL DEFAULT NULL COMMENT '文本结构相似度',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for website_information
-- ----------------------------
DROP TABLE IF EXISTS `website_information`;
CREATE TABLE `website_information`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '网站id',
  `domain` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '网站域名',
  `collection_task_start_time` timestamp(6) NULL DEFAULT NULL COMMENT '采集任务下发时间',
  `collection_task_end_time` timestamp(6) NULL DEFAULT NULL COMMENT '采集任务完成时间',
  `ipv4_addr` json NULL COMMENT 'ipv4地址，json类型，可能存在多个解析记录',
  `ipv6_addr` json NULL COMMENT 'ipv6地址，json类型，可能存在多个解析记录',
  `ipv4_source_code` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT 'ipv4页面源代码',
  `ipv6_source_code` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT 'ipv6页面源代码',
  `ipv4_page_pic` blob NULL COMMENT 'ipv4页面截图',
  `ipv6_page_pic` blob NULL COMMENT 'ipv6页面截图',
  `secondary_links` json NULL COMMENT '二级链接列表',
  `tertiary_links` json NULL COMMENT '三级链接列表',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
