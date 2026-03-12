CREATE TABLE `User` (
  Id               int(10) NOT NULL AUTO_INCREMENT, 
  Uid              varchar(255) NOT NULL, 
  Email            varchar(255) NOT NULL, 
  Name             varchar(255) NOT NULL, 
  ExperiencePoints int(10) NOT NULL, 
  Diamond          int(10) NOT NULL, 
  Password         int(10) NOT NULL,
  Role             varchar(255) NOT NULL DEFAULT 'User',
  CreatedAt        date NOT NULL, 
  LastLogin        timestamp NULL, 
  Avatar           varchar(255), 
  TokenFCM         varchar(255), 
  PRIMARY KEY (Id));
CREATE TABLE Streak (
  Id           bigint(19) NOT NULL AUTO_INCREMENT, 
  LenghtStreak int(10) NOT NULL, 
  StartDate    int(10) NOT NULL, 
  CurentStreak bit(1) NOT NULL, 
  UserId       int(10) NOT NULL, 
  PRIMARY KEY (Id));
CREATE TABLE WordSet (
  Id                     bigint(19) NOT NULL AUTO_INCREMENT, 
  Name                   varchar(255) NOT NULL, 
  Description            varchar(255), 
  CreatedAt              date NOT NULL, 
  IsPublic               bit(1), 
  DefinitionLanguageCode varchar(255) NOT NULL, 
  TermLanguageCode       varchar(255) NOT NULL, 
  UpdatedAt              date, 
  LastOpened             timestamp NULL, 
  UserId                 int(10) NOT NULL, 
  PRIMARY KEY (Id));
CREATE TABLE Word (
  Id              bigint(19) NOT NULL AUTO_INCREMENT, 
  Term            varchar(255) NOT NULL, 
  Definition      varchar(255) NOT NULL, 
  Description     varchar(255), 
  CreatedAt       date NOT NULL, 
  Status          varchar(255) NOT NULL, 
  WordSetId       bigint(19), 
  FlashcardGameId bigint(19) NOT NULL, 
  MatchGameId     int(10) NOT NULL, 
  PRIMARY KEY (Id));
CREATE TABLE FlashcardGame (
  Id        bigint(19) NOT NULL AUTO_INCREMENT, 
  `Mode`    varchar(255) NOT NULL, 
  UpdatedAt date, 
  WordSetId bigint(19) NOT NULL, 
  PRIMARY KEY (Id));
CREATE TABLE UserAchievement (
  Id          bigint(19) NOT NULL AUTO_INCREMENT, 
  Name        varchar(255) NOT NULL, 
  Description varchar(255), 
  EarnedAt    date, 
  Image       varchar(255), 
  UserId      int(10) NOT NULL, 
  PRIMARY KEY (Id));
CREATE TABLE StreakDate (
  Id                     bigint(19) NOT NULL AUTO_INCREMENT, 
  `Date`                 date NOT NULL, 
  ProtectedDate          bit(1), 
  ProtectedBy            varchar(255), 
  ExperiencePointsEarned int(10), 
  StreakId               bigint(19) NOT NULL, 
  PRIMARY KEY (Id));
CREATE TABLE MatchGame (
  Id            int(10) NOT NULL AUTO_INCREMENT, 
  CreatedAt     timestamp NOT NULL, 
  CompletedTime int(10), 
  WordSetId     bigint(19) NOT NULL, 
  PRIMARY KEY (Id));
CREATE TABLE SetencePattern (
  Id                     int(10) NOT NULL AUTO_INCREMENT, 
  Name                   varchar(255) NOT NULL, 
  Description            varchar(255) NOT NULL, 
  CreatedAt              date NOT NULL, 
  IsPublic               bit(1), 
  TermLanguageCode       varchar(255) NOT NULL, 
  DefinitionLanguageCode varchar(255) NOT NULL, 
  UpdateAt               date, 
  LastOpened             timestamp NULL, 
  UserId                 int(10) NOT NULL, 
  PRIMARY KEY (Id));
CREATE TABLE Setence (
  Id               int(10) NOT NULL AUTO_INCREMENT, 
  Term             varchar(255) NOT NULL, 
  Definition       varchar(255) NOT NULL, 
  CreatedAt        date NOT NULL, 
  Status           varchar(255) NOT NULL, 
  NumberOfMistakes int(10), 
  SetencePatternId int(10) NOT NULL, 
  PRIMARY KEY (Id));
CREATE TABLE WritingGame (
  Id               int(10) NOT NULL AUTO_INCREMENT, 
  CreatedAt        timestamp NULL, 
  CompletedTime    timestamp NULL, 
  SetencePatternId int(10) NOT NULL, 
  PRIMARY KEY (Id));
CREATE TABLE Setting (
  Id           int(10) NOT NULL AUTO_INCREMENT, 
  Notification bit(1) NOT NULL, 
  Language     varchar(255), 
  UserId       int(10) NOT NULL, 
  PRIMARY KEY (Id));
CREATE TABLE Item (
  Id              int(10) NOT NULL AUTO_INCREMENT, 
  WaterStreak     int(10) NOT NULL, 
  SuperExperience int(10) NOT NULL, 
  HackExperience  int(10) NOT NULL, 
  UserId          int(10) NOT NULL, 
  PRIMARY KEY (Id));
CREATE TABLE Video (
  Id         int(10) NOT NULL AUTO_INCREMENT, 
  Title      varchar(255) NOT NULL, 
  Thumbnail  varchar(255) NOT NULL, 
  SourceUrl  varchar(255) NOT NULL, 
  LastOpened timestamp NULL, 
  TypeVideo  int(10), 
  CreatedAt  date, 
  UserId     int(10), 
  PRIMARY KEY (Id));
CREATE TABLE Subtitle (
  Id        int(10) NOT NULL AUTO_INCREMENT, 
  SourceUrl int(10) NOT NULL, 
  VideoId   int(10) NOT NULL, 
  PRIMARY KEY (Id));
ALTER TABLE Streak ADD CONSTRAINT FKStreak329675 FOREIGN KEY (UserId) REFERENCES `User` (Id);
ALTER TABLE WordSet ADD CONSTRAINT FKWordSet74244 FOREIGN KEY (UserId) REFERENCES `User` (Id);
ALTER TABLE FlashcardGame ADD CONSTRAINT FKFlashcardG699910 FOREIGN KEY (WordSetId) REFERENCES WordSet (Id);
ALTER TABLE UserAchievement ADD CONSTRAINT FKUserAchiev787107 FOREIGN KEY (UserId) REFERENCES `User` (Id);
ALTER TABLE Word ADD CONSTRAINT FKWord892291 FOREIGN KEY (WordSetId) REFERENCES WordSet (Id);
ALTER TABLE StreakDate ADD CONSTRAINT FKStreakDate824617 FOREIGN KEY (StreakId) REFERENCES Streak (Id);
ALTER TABLE MatchGame ADD CONSTRAINT FKMatchGame814848 FOREIGN KEY (WordSetId) REFERENCES WordSet (Id);
ALTER TABLE Word ADD CONSTRAINT FKWord989206 FOREIGN KEY (FlashcardGameId) REFERENCES FlashcardGame (Id);
ALTER TABLE Item ADD CONSTRAINT FKItem227668 FOREIGN KEY (UserId) REFERENCES `User` (Id);
ALTER TABLE Setence ADD CONSTRAINT FKSetence294133 FOREIGN KEY (SetencePatternId) REFERENCES SetencePattern (Id);
ALTER TABLE WritingGame ADD CONSTRAINT FKWritingGam602527 FOREIGN KEY (SetencePatternId) REFERENCES SetencePattern (Id);
ALTER TABLE SetencePattern ADD CONSTRAINT FKSetencePat143848 FOREIGN KEY (UserId) REFERENCES `User` (Id);
ALTER TABLE Video ADD CONSTRAINT FKVideo866843 FOREIGN KEY (UserId) REFERENCES `User` (Id);
ALTER TABLE Subtitle ADD CONSTRAINT FKSubtitle235120 FOREIGN KEY (VideoId) REFERENCES Video (Id);
ALTER TABLE Setting ADD CONSTRAINT FKSetting80873 FOREIGN KEY (UserId) REFERENCES `User` (Id);
