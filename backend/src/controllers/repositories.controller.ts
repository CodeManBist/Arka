import { Request, Response } from "express";
import { isValidGitHubUrl } from "../utils/github.ts";
import { cloneRepository } from "../services/repository.service.ts";

export const cloneRepositoryController = async (req: Request, res: Response) => {
    try {
        const { repositoryUrl } = req.body;

        if(!repositoryUrl) {
            return res.status(400).json({ 
                success: false, 
                message: "Repository URL is required" 
            });
        }

        if(!isValidGitHubUrl(repositoryUrl)) {
            return res.status(400).json({ 
                success: false, 
                message: "Invalid GitHub repository URL" 
            });
        }

        const repository = await cloneRepository(repositoryUrl);

        res.status(200).json({
            success: true,
            message: "Repository cloned successfully",
            data: repository
        });
    } catch (error) {   
        res.status(500).json({
            success: false,
            message: error instanceof Error ? error.message : "An unexpected error occurred"
        });
    }
};