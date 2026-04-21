using UnityEngine;
using UnityEngine.UIElements;
public class UIController : MonoBehaviour
{
    [Header("References")]
    [SerializeField] private UIDocument  uiDocument;
    [SerializeField] private PointSpawner pointSpawner;

    private Label rankDisplay;
    private Label spacingVal;
    private Label alphaVal;
    private Label pointCounter;

    private int currentPointIndex = 0;
    private int totalPoints       = 0; 

    private readonly string[] ranks =
    {
        "IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM",
        "EMERALD", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"
    };

    void OnEnable()
    {
        var root = uiDocument.rootVisualElement;

        rankDisplay  = root.Q<Label>("rank-display");
        spacingVal   = root.Q<Label>("spacing-val");
        alphaVal     = root.Q<Label>("alpha-val");
        pointCounter = root.Q<Label>("point-counter");

        var rankSlider = root.Q<Slider>("rank-slider");
        rankSlider.RegisterValueChangedCallback(evt =>
        {
            int index = Mathf.RoundToInt(evt.newValue);
            index = Mathf.Clamp(index, 0, ranks.Length - 1);

            rankDisplay.text = ranks[index];
            pointSpawner.OnRankSliderChanged(index);
        });

        var spacingSlider = root.Q<Slider>("spacing-slider");
        spacingSlider.RegisterValueChangedCallback(evt =>
        {
            spacingVal.text = evt.newValue.ToString("F1");
            pointSpawner.UpdateSpacing(evt.newValue);
        });

        var alphaSlider = root.Q<Slider>("alpha-slider");
        alphaSlider.RegisterValueChangedCallback(evt =>
        {
            alphaVal.text = evt.newValue.ToString("F2");
            pointSpawner.UpdateAlpha(evt.newValue);
        });

        root.Q<Button>("prev-btn").clicked += () =>
        {
            pointSpawner.previousPoint();
            currentPointIndex = Mathf.Max(0, currentPointIndex - 1);
            RefreshPointCounter();
        };

        root.Q<Button>("next-btn").clicked += () =>
        {
            pointSpawner.nextPoint();
            currentPointIndex++;
            RefreshPointCounter();
        };

        root.Q<Button>("back-btn").clicked += () => pointSpawner.BackToInput();
    }


    /// Call once after the API response arrives so the status bar shows real counts.
    public void SetStatusBar(int points, int clusters, int noise, string lane)
    {
        var root = uiDocument.rootVisualElement;

        root.Q<Label>("sb-points")  .text = $"POINTS: {points:N0}";
        root.Q<Label>("sb-clusters").text = $"CLUSTERS: {clusters}";
        root.Q<Label>("sb-noise")   .text = $"NOISE: {noise:N0}";
        root.Q<Label>("header-lane").text = $"LANE: {lane.ToUpper()}";

        totalPoints = points;
        RefreshPointCounter();
    }

    private void RefreshPointCounter()
    {
        if (pointCounter == null) return;
        string total = totalPoints > 0 ? totalPoints.ToString("N0") : "?";
        pointCounter.text = $"POINT  //  {(currentPointIndex + 1):D4}  of  {total}";
    }
}
