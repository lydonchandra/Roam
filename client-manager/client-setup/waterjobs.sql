SET ANSI_NULLS, QUOTED_IDENTIFIER ON;
INSERT INTO WaterJobs (
         [ogr_geometry]
      ,[CustomerRequestNumber]
      ,[DateTimeReceived]
      ,[RequestedBy]
      ,[RequestType]
      ,[AdditionalLocationDetails]
      ,[StreetNumber]
      ,[Street]
      ,[Operators]
      ,[RespondTime]
      ,[CompletionTime]
      ,[ConnectionsInterrupted]
      ,[InterruptionDurationHours]
      ,[ConsumerContacted]
      ,[FollowUpWorkRequired]
      ,[ShutdownLetter]
      ,[ShutdownDoorknock]
      ,[MainRepairedClamp]
      ,[MainRepairedReplacedSection]
      ,[FailureType]
      ,[HydrantRepair]
      ,[HydrantReplace]
      ,[HydrantCleanAndMark]
      ,[HydrantReplaceLid]
      ,[MainsValveRepair]
      ,[MainsValveReplace]
      ,[ReplaceLidValve]
      ,[ReplaceMarkers]
      ,[RepairedServiceClamp]
      ,[RepairedServiceReplaceSection]
      ,[ReplacedStopCock]
      ,[RepairedStopCock]
      ,[TpfnrRepaired]
      ,[TpfnrReplaced]
      ,[TpfnrCapped]
      ,[PressureTestService]
      ,[PressureTestHydrant]
      ,[LockupKpa]
      ,[TestSheetCompleted]
      ,[HydrantFlowTest]
      ,[ServiceFlowTest]
      ,[LitresPerMinute]
      ,[Investigate]
      ,[ConsumerProblem]
      ,[CouncilFacility]
      ,[ProvideLocation]
      ,[BackfillsCleanups]
      ,[WaterSample]
      ,[MainsFlushed]
      ,[MeterCover]
      ,[Other]
      ,[InstallationSheetNumber]
      ,[NewService]
      ,[FireService]
      ,[RelayedService]
      ,[MeterReplaced]
      ,[MeterRemoved]
      ,[DisconnectService]
      ,[MeterRead]
      ,[ExistingMeterNumber]
      ,[ExistingMeterReadingKL]
      ,[NewMeterNumber]
      ,[NewMeterReadingKL]
      ,[PipeMaterial]
      ,[PipeDiameter]
      ,[PipeDepth]
      ,[JointType]
      ,[GroundConditions]
      ,[ValveType]
      ,[ValveStatus]
      ,[ValveClosingDirection]
      ,[Designation]
      ,[Scheme]
      ,[TrafficControlPlanUsed]
      ,[WorkDurationHours]
      ,[SignageAlterations]
      ,[Drawing]
      ,[WorkMethodStatement]
      ,[Notes]
      ,[MainsAndFittingsGroup]
      ,[ServiceRepairsGroup]
      ,[PressureAndFlowGroup]
      ,[OtherGroup]
      ,[InstallationsAndMeterReadsGroup]
      ,[AssetinformationGroup]
      ,[LotPlan])
SELECT [ogr_geometry]
      ,[CustomerRequestNumber]
      ,[DateTimeReceived]
      ,[RequestedBy]
      ,[RequestType]
      ,[AdditionalLocationDetails]
      ,[StreetNumber]
      ,[Street]
      ,[Operators]
      ,[RespondTime]
      ,[CompletionTime]
      ,[ConnectionsInterrupted]
      ,[InterruptionDurationHours]
      ,[ConsumerContacted]
      ,[FollowUpWorkRequired]
      ,[ShutdownLetter]
      ,[ShutdownDoorknock]
      ,[MainRepairedClamp]
      ,[MainRepairedReplacedSection]
      ,[FailureType]
      ,[HydrantRepair]
      ,[HydrantReplace]
      ,[HydrantCleanAndMark]
      ,[HydrantReplaceLid]
      ,[MainsValveRepair]
      ,[MainsValveReplace]
      ,[ReplaceLidValve]
      ,[ReplaceMarkers]
      ,[RepairedServiceClamp]
      ,[RepairedServiceReplaceSection]
      ,[ReplacedStopCock]
      ,[RepairedStopCock]
      ,[TpfnrRepaired]
      ,[TpfnrReplaced]
      ,[TpfnrCapped]
      ,[PressureTestService]
      ,[PressureTestHydrant]
      ,[LockupKpa]
      ,[TestSheetCompleted]
      ,[HydrantFlowTest]
      ,[ServiceFlowTest]
      ,[LitresPerMinute]
      ,[Investigate]
      ,[ConsumerProblem]
      ,[CouncilFacility]
      ,[ProvideLocation]
      ,[BackfillsCleanups]
      ,[WaterSample]
      ,[MainsFlushed]
      ,[MeterCover]
      ,[Other]
      ,[InstallationSheetNumber]
      ,[NewService]
      ,[FireService]
      ,[RelayedService]
      ,[MeterReplaced]
      ,[MeterRemoved]
      ,[DisconnectService]
      ,[MeterRead]
      ,[ExistingMeterNumber]
      ,[ExistingMeterReadingKL]
      ,[NewMeterNumber]
      ,[NewMeterReadingKL]
      ,[PipeMaterial]
      ,[PipeDiameter]
      ,[PipeDepth]
      ,[JointType]
      ,[GroundConditions]
      ,[ValveType]
      ,[ValveStatus]
      ,[ValveClosingDirection]
      ,[Designation]
      ,[Scheme]
      ,[TrafficControlPlanUsed]
      ,[WorkDurationHours]
      ,[SignageAlterations]
      ,[Drawing]
      ,[WorkMethodStatement]
      ,[Notes]
      ,[MainsAndFittingsGroup]
      ,[ServiceRepairsGroup]
      ,[PressureAndFlowGroup]
      ,[OtherGroup]
      ,[InstallationsAndMeterReadsGroup]
      ,[AssetinformationGroup]
      ,[LotPlan] FROM WaterJobs_old old
      WHERE NOT EXISTS (SELECT * FROM WaterJobs j
                                 WHERE j.UniqueID = old.UniqueID);