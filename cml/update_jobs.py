import os

import cmlapi

GENERATE_DATA_JOB_NAME = "generate data"
PULL_GIT_JOB_NAME = "pull git"
LOAD_DATA_JOB_NAME = "load data"
RETRAIN_MODEL_JOB_NAME = "retrain model"
DEPLOY_MODEL_JOB_NAME = "deploy model"
MODEL_SIMULATION_JOB_NAME = "run simulation"

if __name__ == "__main__":
    client = cmlapi.default_client(
        url=os.getenv("CDSW_API_URL").replace("/api/v1", ""),
        cml_api_key=os.getenv("CDSW_APIV2_KEY"),
    )

    project = client.get_project(project_id=os.getenv("CDSW_PROJECT_ID"))
    jobs_list = client.list_jobs(project.id)

    generate_data_job = None
    pull_git_job = None
    load_data_job = None
    retrain_model_job = None
    deploy_model_job = None
    model_simulation_job = None

    for j in jobs_list.jobs:
        job_name = j.name.lower()

        if GENERATE_DATA_JOB_NAME == job_name:
            generate_data_job = j
            continue
        if PULL_GIT_JOB_NAME == job_name:
            pull_git_job = j
            continue
        if LOAD_DATA_JOB_NAME == job_name:
            load_data_job = j
            continue
        if RETRAIN_MODEL_JOB_NAME == job_name:
            retrain_model_job = j
            continue
        if DEPLOY_MODEL_JOB_NAME == job_name:
            deploy_model_job = j
            continue
        if MODEL_SIMULATION_JOB_NAME == job_name:
            model_simulation_job = j
            continue

    for x in [
        generate_data_job,
        pull_git_job,
        load_data_job,
        retrain_model_job,
        deploy_model_job,
        model_simulation_job,
    ]:
        assert x is not None, f'job "{x}" not found'

    client.update_job(
        project_id=project.id,
        job_id=pull_git_job.id,
        body={"type": "cron", "schedule": "*/10 * * * *"},
    )

    client.update_job(
        project_id=project.id,
        job_id=model_simulation_job.id,
        body={"type": "dependent", "parent_id": deploy_model_job.id},
    )

    client.update_job(
        project_id=project.id,
        job_id=deploy_model_job.id,
        body={"type": "dependent", "parent_id": retrain_model_job.id},
    )

    client.update_job(
        project_id=project.id,
        job_id=retrain_model_job.id,
        body={"type": "dependent", "parent_id": load_data_job.id},
    )

    client.update_job(
        project_id=project.id,
        job_id=load_data_job.id,
        body={"type": "cron", "schedule": "*/30 * * * *"},
    )
