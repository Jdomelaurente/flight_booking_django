/**
 * Shared grading logic to ensure consistency between the submissions table and the analysis view.
 */

export const GRADING_THRESHOLDS = {
    accuracy: [
        { threshold: 1.0, level: 5, status: 'Excellent' },
        { threshold: 0.8, level: 4, status: 'Very Good' },
        { threshold: 0.5, level: 3, status: 'Satisfactory' },
        { threshold: 0.2, level: 2, status: 'Needs Improvement' },
        { threshold: 0.0, level: 1, status: 'Poor' }
    ],
    tech: [
        { threshold: 1.0, level: 5, status: 'Excellent' },
        { threshold: 0.7, level: 4, status: 'Very Good' },
        { threshold: 0.4, level: 3, status: 'Satisfactory' },
        { threshold: 0.1, level: 2, status: 'Needs Improvement' },
        { threshold: 0.0, level: 1, status: 'Poor' }
    ],
    org: [
        { threshold: 1.0, level: 5, status: 'Excellent' },
        { threshold: 0.8, level: 4, status: 'Very Good' },
        { threshold: 0.5, level: 3, status: 'Satisfactory' },
        { threshold: 0.2, level: 2, status: 'Needs Improvement' },
        { threshold: 0.0, level: 1, status: 'Poor' }
    ],
    comp: [
        { threshold: 1.0, level: 5, status: 'Excellent' },
        { threshold: 0.5, level: 3, status: 'Satisfactory' },
        { threshold: 0.01, level: 2, status: 'Needs Improvement' },
        { threshold: 0.0, level: 1, status: 'Poor' }
    ],
    prof: [
        { threshold: 1.0, level: 5, status: 'Excellent' },
        { threshold: 0.7, level: 4, status: 'Very Good' },
        { threshold: 0.4, level: 3, status: 'Satisfactory' },
        { threshold: 0.1, level: 2, status: 'Needs Improvement' },
        { threshold: 0.0, level: 1, status: 'Poor' }
    ]
};

/**
 * Normalizes trip type strings to canonical snake_case codes.
 */
export const normalizeTripTypeToCode = (str) => {
    return (str || '').toLowerCase().trim().replace(/[\s-]+/g, '_');
};

/**
 * Compares strings with fuzzy support.
 */
export const compareStrings = (a, b) => {
    const s1 = (a || '').toString().trim().toLowerCase();
    const s2 = (b || '').toString().trim().toLowerCase();
    if (s1 === s2) return true;
    if (s1 && s2) {
        if (s1.length >= 2 && s2.length >= 2) {
            if (s1.includes(s2) || s2.includes(s1)) return true;
        }
    }
    return false;
};

/**
 * Calculates aLevel based on ratio and rubric type.
 */
export const calculateLevel = (ratio, type) => {
    const thresholds = GRADING_THRESHOLDS[type] || GRADING_THRESHOLDS.accuracy;
    for (const t of thresholds) {
        if (ratio >= t.threshold) {
            return { level: t.level, status: t.status };
        }
    }
    return { level: 1, status: 'Poor' };
};

/**
 * Calculates the total grade points (0 to totalPoints).
 */
export const calculateTotalGrade = (analysis, totalPoints = 100) => {
    if (!analysis) return 0;
    
    const accuracyRatio = analysis.accuracy ?? 0;
    const techRatio = analysis.tech ?? 0;
    const orgRatio = analysis.org ?? 0;
    const compRatio = analysis.comp ?? 0;
    const profRatio = analysis.prof ?? 0;
    
    const sumOfRatios = accuracyRatio + techRatio + orgRatio + compRatio + profRatio;
    return sumOfRatios * (totalPoints / 5);
};

/**
 * Formats a grade into a rounded percentage (0-100).
 */
export const calculatePercentage = (score, totalPoints = 100) => {
    if (!totalPoints || totalPoints === 0) return 0;
    // We use Math.round of the full percentage to match instructor_student_score's visual display.
    return Math.round((score / totalPoints) * 100);
};

/**
 * Performs a detailed assessment calculation mirroring the Assessment Analysis View logic.
 */
export const performDetailedAssessment = (activity, submission) => {
    if (!activity || !submission) return null;
    
    // We use the already-provided sub.analysis (backend) OR sub.grade if it exists.
    // If sub.grade exists, we assume it is the "truth" saved by the instructor.
    // If not, we use sub.analysis to calculate the preview.
    
    const totalPoints = parseFloat(activity.total_points || 100);
    const analysis = submission.analysis || {};
    
    const score = submission.grade !== null 
        ? parseFloat(submission.grade) 
        : calculateTotalGrade(analysis, totalPoints);
    
    const percentage = calculatePercentage(score, totalPoints);
    
    return {
        score,
        percentage,
        analysis: analysis
    };
};
