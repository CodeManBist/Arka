import simpleGit from "simple-git";
import fs from "fs";
import path from "path";

const git = simpleGit();

export const cloneRepository = async (repositoryUrl: string) => {
    const repoName = repositoryUrl
        .split('/')
        .pop()
        ?.replace('.git', "");

    if(!repoName) {
        throw new Error("Unable to determine repository name from URL");
    }

    const repositoriesDir = path.join(process.cwd(), "repositories");

    if(!fs.existsSync(repositoriesDir)) {
        fs.mkdirSync(repositoriesDir);
    }

    const destination = path.join(repositoriesDir, repoName);

    if(fs.existsSync(destination)) {
        throw new Error(`Repository ${repoName} already exists`);
    }

    await git.clone(repositoryUrl, destination);

    return {
        repositoryName: repoName,
        path: destination,
    };
};