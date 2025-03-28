IMPORT ML_Core;
IMPORT ML_Unsupervised;

// Preprocessing for Clustering
ClusteringPrep := PROJECT(File_AllData.mc_byStateDS,
    TRANSFORM({
        UNSIGNED1 age; 
        UNSIGNED2 stateCode; 
        UNSIGNED4 recordCount
    },
    SELF.age := LEFT.CurrentAge,
    SELF.stateCode := IF(LEFT.MissingState = '', 0, HASH32(LEFT.MissingState)),
    SELF.recordCount := 1
    )
);

// Aggregate Data for Clustering
ClusteringData := TABLE(ClusteringPrep,
    {
        age,
        stateCode,
        UNSIGNED recordCount := SUM(GROUP, recordCount)
    },
    age, stateCode
);

// Machine Learning Clustering
ClusterModel := ML_Unsupervised.KMeans(3, ClusteringData);

// Roxie Service for Filtering and Clustering
EXPORT RoxieService(
    INTEGER2 in_minAge = 0, 
    INTEGER2 in_maxAge = 18, 
    STRING2 in_state = ''
) := FUNCTION
    // Filter the original dataset
    Filtered := File_AllData.mc_byStateDS(
        (in_state = '' OR MissingState = in_state) AND
        (CurrentAge >= in_minAge AND CurrentAge <= in_maxAge)
    );

    // Join filtered data with cluster model
    ClusteredFiltered := JOIN(Filtered, ClusterModel,
        LEFT.CurrentAge = RIGHT.age AND 
        HASH32(LEFT.MissingState) = RIGHT.stateCode,
        TRANSFORM({
            RECORDOF(Filtered), 
            UNSIGNED1 ClusterID := 0
        },
            SELF := LEFT,
            SELF.ClusterID := IF(EXISTS(RIGHT), RIGHT.Cluster, 0)
        ),
        LEFT OUTER
    );

    RETURN OUTPUT(ClusteredFiltered, NAMED('ClusteredFilteredResults'));
END;

// Alias for easier calling
EXPORT RoxieQuery := RoxieService;