ALTER TABLE `reports_bug_class` ADD COLUMN `total_bug` integer DEFAULT 0 NOT NULL COMMENT 'bug总计';
ALTER TABLE `reports_bug_class` ALTER COLUMN `total_bug` DROP DEFAULT;
