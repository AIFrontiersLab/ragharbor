import json

from answer_or_abstain_rag.adapters.inbound.cli.main import main


def test_run_describe_config_doctor(tmp_path, capsys, make_request):
    request = tmp_path / "req.json"
    request.write_text(json.dumps(make_request()))
    assert main(["run", str(request)]) == 0
    assert json.loads(capsys.readouterr().out)["status"] in {"completed", "awaiting_approval"}
    assert main(["describe"]) == 0
    assert json.loads(capsys.readouterr().out)["stages"]
    assert main(["config"]) == 0
    assert "pipeline" in json.loads(capsys.readouterr().out)
    assert main(["doctor"]) == 0


def test_run_with_corpus(tmp_path, capsys):
    corpus = tmp_path / "corpus.json"
    corpus.write_text(json.dumps([{"doc_id": "k1", "text": "token budget enforcement", "classification": "public"}]))
    request = tmp_path / "req.json"
    request.write_text(json.dumps({"query": "token budget"}))
    assert main(["run", str(request), "--corpus", str(corpus)]) == 0
    assert json.loads(capsys.readouterr().out)["answer"]["evidence_ids"] == ["k1"]


def test_errors_exit_nonzero(tmp_path, capsys):
    request = tmp_path / "req.json"
    request.write_text(json.dumps({"query": ""}))
    assert main(["run", str(request)]) == 2
    assert "validation_error" in capsys.readouterr().err
