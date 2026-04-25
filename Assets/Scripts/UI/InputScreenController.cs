using System.Collections;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UIElements;

public class InputScreenController : MonoBehaviour
{
    [SerializeField] private UIDocument uiDocument;
    private APIHandler apiHandler;

    private readonly string[] laneNames = { "TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY" };
    private string selectedLane = "TOP";

    private VisualElement root;
    private Button submitBtn;
    private Label  loadingLabel;
    private VisualElement loadingBar;
    private Label  errorLabel;

    void Start()
    {
        root = uiDocument.rootVisualElement;
        apiHandler = GameObject.Find("API").GetComponent<APIHandler>();

        foreach (var lane in laneNames)
        {
            var captured = lane;
            var btn = root.Q<Button>($"lane-{lane}");
            if (btn != null)
                btn.clicked += () => SelectLane(captured);
        }

        submitBtn = root.Q<Button>("submit-btn");
        submitBtn.clicked += OnSubmit;

        root.Q<Button>("back-btn").clicked += loadMenu;

        loadingLabel = root.Q<Label>("loading-label");
        loadingBar   = root.Q<VisualElement>("loading-bar");
        errorLabel   = root.Q<Label>("id-error");

        var field = root.Q<TextField>("riot-id-field");
        field?.RegisterCallback<KeyDownEvent>(evt =>
        {
            if (evt.keyCode == KeyCode.Return || evt.keyCode == KeyCode.KeypadEnter)
                OnSubmit();
        });
    }

    void loadMenu()
    {
        SceneManager.LoadScene("Menu");
    }

    void SelectLane(string lane)
    {
        selectedLane = lane;

        foreach (var l in laneNames)
        {
            var btn = root.Q<Button>($"lane-{l}");
            if (btn == null) continue;

            if (l == lane)
                btn.AddToClassList("lane-active");
            else
                btn.RemoveFromClassList("lane-active");
        }
    }

    void OnSubmit()
    {
        Debug.Log("test");
        errorLabel.text = "";
        var field = root.Q<TextField>("riot-id-field");
        string rawInput = field?.value?.Trim() ?? "";

        if (string.IsNullOrEmpty(rawInput) || !rawInput.Contains("#"))
        {
            errorLabel.text = "!  INVALID FORMAT  —  USE  Name#Tag";
            return;
        }

        string[] parts = rawInput.Split('#');
        if (parts.Length != 2 || string.IsNullOrEmpty(parts[0]) || string.IsNullOrEmpty(parts[1]))
        {
            errorLabel.text = "!  INVALID FORMAT  —  USE  Name#Tag";
            return;
        }

        string name = parts[0];
        string tag  = parts[1];

        SetLoadingState(true);


        apiHandler.SubmitFromUI(name, tag, selectedLane,
        onSuccess: () => SetLoadingState(false),
        onError:   err =>
        {
            SetLoadingState(false);
            errorLabel.text = $"!  {err.ToUpper()}";
        });
    }

    void SetLoadingState(bool isLoading)
    {
        submitBtn.SetEnabled(!isLoading);

        if (isLoading)
        {
            loadingBar.RemoveFromClassList("loading-hidden");
            loadingLabel.text = "FETCHING DATA...";
            StartCoroutine(AnimateLoadingBar());
        }
        else
        {
            loadingBar.AddToClassList("loading-hidden");
            loadingLabel.text = "";
            StopAllCoroutines();
        }
    }

    IEnumerator AnimateLoadingBar()
    {
        var fill   = loadingBar.Q<VisualElement>(className: "loading-fill");
        float t    = 0f;
        bool  ping = true;

        while (true)
        {
            t += Time.deltaTime * (ping ? 1f : -1f) * 0.9f;
            if (t >= 1f) { t = 1f; ping = false; }
            if (t <= 0f) { t = 0f; ping = true;  }

            float pct = Mathf.Lerp(10f, 90f, t);
            fill.style.width = Length.Percent(pct);

            yield return null;
        }
    }
}