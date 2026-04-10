# MDA Intent Layer -- User Guide

*A step-by-step guide for document owners working with the MDA Intent Layer.*

---

## What Is This?

You own business processes. Maybe you manage how income verification works, or how
loan applications get approved, or how property appraisals are reviewed. Right now,
those processes probably live in flowcharts, Word documents, and the heads of
experienced employees.

The **MDA Intent Layer** takes those flowcharts (specifically, BPMN diagrams) and
converts them into structured documents that AI agents can read and execute. Think of
it as translating a process manual into a format that software can follow step by
step.

**Your job** is to make sure those generated documents accurately describe how the
business actually works. You review them, fill in details, fix mistakes, and submit
your changes for approval -- much like editing a document and sending it to your
manager for sign-off.

You will do all of this in a program called **VS Code**, which is a text editor. If
you have used Word or Notepad, you already understand the basic idea: you open files,
you read them, you type changes, and you save. VS Code just looks a little different.

You do **not** need to write code. You do **not** need to understand programming.
You are editing plain-English documents that happen to live in a structured format.

---

## What You Will Need

### Software to Install (One-Time Setup)

You need three programs installed on your computer. If your IT department manages
your machine, ask them to install these for you.

#### 1. VS Code -- Your Text Editor

VS Code is the program where you will open and edit your process documents. It works
like Word, but for plain-text files.

- **Download:** Go to <https://code.visualstudio.com> in your web browser
- **Install:** Run the downloaded file and click "Next" through the installer,
  accepting the default options
- **Open it:** Find "Visual Studio Code" in your Start menu and open it

> **Tip:** VS Code is free. It is made by Microsoft. It is not the same as
> "Visual Studio" (which is a different, larger program).

#### 2. Python -- The Engine Behind the Tools

Python is a programming language that powers the tools you will use. You will not
write Python code -- you just need it installed so the tools can run.

- **Download:** Go to <https://www.python.org/downloads/> and click the big
  "Download Python" button
- **Install:** Run the downloaded file. **On the very first screen of the
  installer, there is a checkbox at the bottom that says "Add Python to PATH".
  Check that box.** Then click "Install Now" and wait for it to finish.

> **Why "Add to PATH" matters:** This lets your computer find Python when you type
> commands. If you skip this step, nothing will work and you will see an error
> that says "python is not recognized." If that happens, uninstall Python and
> reinstall it with the checkbox checked.

- **Verify it worked:** Open VS Code, then press **Ctrl+\`** (the backtick key,
  located above the Tab key on most keyboards). This opens a panel at the bottom
  of VS Code called the **Terminal**. Type the following and press Enter:

  ```
  python --version
  ```

  You should see something like `Python 3.12.4`. If you see an error instead,
  Python is not installed correctly.

#### 3. Git -- Change Tracking for Your Documents

Git tracks every change you make to your documents, like the "Track Changes"
feature in Word. It also lets you submit your changes for review and keeps a
history of every edit anyone has ever made.

- **Download:** Go to <https://git-scm.com/downloads> and download the version
  for your operating system
- **Install:** Run the downloaded file and accept all the default options
- **Verify it worked:** In the VS Code terminal (Ctrl+\`), type:

  ```
  git --version
  ```

  You should see something like `git version 2.44.0`.

#### 4. (Optional) An AI Coding Assistant

If your organization uses an AI assistant like **Claude Code**, **GitHub Copilot**,
or **Cursor**, it can help you run commands by typing plain-English requests
instead of memorizing command syntax. For example, you could type "show me the
status of my process" and the assistant would run the right command for you.

This is entirely optional. Every command in this guide can be typed manually.

---

### Get the Project (One-Time Setup)

Now you need to download the project files to your computer. Open the VS Code
terminal (Ctrl+\`) and type these three commands, pressing Enter after each one:

```
git clone https://github.com/Chunkys0up7/ISLayer.git
```

**What this does:** Downloads all the project files from the shared repository to
a new folder called `ISLayer` on your computer. Think of it as downloading a shared
folder from the cloud.

```
cd ISLayer
```

**What this does:** Moves you into the project folder. "cd" stands for "change
directory" -- it is like double-clicking a folder to open it.

```
pip install -r requirements.txt
```

**What this does:** Installs the additional software libraries that the project
tools need. "pip" is Python's tool for installing add-ons. The file
`requirements.txt` contains a list of everything needed.

> **Tip:** If `pip` gives an error, try `pip3 install -r requirements.txt` instead.

#### Open the Project in VS Code

1. In VS Code, go to **File > Open Folder**
2. Navigate to the `ISLayer` folder you just downloaded
3. Click "Select Folder"

You should now see the project files listed in the left-hand panel of VS Code.

---

### Verify Everything Works

Before you start working, confirm that the tools are functioning. In the terminal,
type:

```
python cli/mda.py test --quick
```

If you see a message that says **"6 passed"** (or a similar count with all passing),
you are ready to go.

If you see errors, check that Python and the dependencies are installed correctly
(see the troubleshooting section at the end of this guide).

---

## Your Workspace

When you open the project in VS Code, you will see a list of folders in the left
panel. Here is what each one contains:

| Folder | What It Is | Do You Edit It? |
|--------|-----------|-----------------|
| `examples/` | Demo processes to learn from (like sample documents) | Yes -- this is where you work |
| `corpus/` | The knowledge library: procedures, policies, regulations, glossary terms | Yes -- you add and update knowledge documents |
| `cli/` | The tools that check your work and process commands | No -- do not edit these |
| `schemas/` | The rules that define what valid documents look like | No -- do not edit these |
| `templates/` | Blank document templates used when creating new files | No -- do not edit these |
| `docs/` | Documentation and guides (like this one) | No |
| `tests/` | Automated checks that verify everything is correct | No |

### What the Documents Look Like

The main documents you work with are called **capsule files**. They have the file
extension `.cap.md`. Here is a simplified example:

```
---
capsule_id: "CAP-IV-W2V-001"
bpmn_task_id: "Task_VerifyW2"
bpmn_task_name: "Verify W-2 Income"
process_id: "Process_IncomeVerification"
version: "1.0"
status: "draft"
domain: "Mortgage Lending"
predecessor_ids:
  - "CAP-IV-DEC-001"
successor_ids:
  - "CAP-IV-QAL-001"
gaps:
  - type: "missing_detail"
    description: "OCR confidence threshold not yet defined"
    severity: "low"
---

# Verify W-2 Income

## Purpose

Validates the borrower's W-2 wage income by cross-referencing
employer-issued W-2 forms against IRS tax return transcripts.

## Procedure

1. Retrieve W-2 documents from DocVault for the most recent
   two tax years.
2. Retrieve IRS Form 1040 data for the same tax years.
3. Compare the sum of all W-2 Box 1 amounts to the 1040 Line 1 amount.
4. Flag discrepancies for manual review.

## Business Rules

- Income declined by more than 10% requires using the lower year.
- Additional compensation above 25% of base pay requires 2-year history.
```

Let's break that down:

- **The `---` block at the top** is called the "front matter." It contains metadata
  -- properties about the document, like its ID, which process it belongs to, and
  what comes before and after it in the workflow. Think of it like the "Document
  Properties" dialog in Word. **You generally do not edit this section.** The tools
  manage it for you.

- **Everything below the second `---`** is the content -- the actual description of
  the business task. **This is what you edit.** It is written in a format called
  Markdown, which uses simple symbols like `#` for headings, `-` for bullet points,
  and `1.` for numbered lists.

- **The `gaps` section** in the front matter lists known holes in the documentation.
  The tools identify these automatically. Your job is to fill them in by adding the
  missing information to the content sections below.

---

## Working with Your Process

Each business process lives in its own folder. For example, the income verification
process lives in `examples/income-verification/`. Let's walk through the basic
workflow.

### Step 1: Navigate to Your Process

In the VS Code terminal, type:

```
cd examples/income-verification
```

This moves you into the income verification process folder. If your process has a
different name, replace `income-verification` with your process folder name.

> **Tip:** You can also navigate by clicking folders in the left-hand panel of
> VS Code. But for running commands, you need to be in the right folder in the
> terminal.

### Step 2: See What Is There

```
python ../../cli/mda.py status
```

This shows you a table listing every task in your process, along with its current
status (draft, review, approved, etc.).

> **What does `../../cli/mda.py` mean?** The `../..` means "go up two folders."
> You are inside `examples/income-verification/`, and the tools are in `cli/` at
> the project root. So `../../cli/mda.py` tells the computer: "go up to `examples/`,
> then up again to the project root, then into `cli/`, and run `mda.py`."

### Step 3: View the Process Flow

```
python ../../cli/mda.py graph --format mermaid
```

This shows you how the tasks in your process connect to each other -- which task
comes first, what happens next, and where the process branches or merges. It
produces a text-based diagram you can read in the terminal or paste into a
diagramming tool.

### Step 4: Check the Health of Your Process

```
python ../../cli/mda.py report --format yaml
```

This generates a health report for your process. Each task gets a grade:

| Grade | Meaning |
|-------|---------|
| **A** | Excellent -- fully documented, no gaps |
| **B** | Good -- minor details could be improved |
| **C** | Acceptable -- some gaps need attention |
| **D** | Needs work -- significant information is missing |
| **F** | Critical -- major gaps that must be addressed |

---

## Ingesting a New BPMN Diagram

If you have a new BPMN diagram (a `.bpmn` file exported from your process modeling
tool), you can feed it into the system to generate draft documents for every task.

### If You Have a BPMN File

1. Copy your `.bpmn` file into the `bpmn/` folder inside your process directory
2. In the terminal, run:

   ```
   python ../../cli/mda.py ingest bpmn/your-file.bpmn --skip-llm
   ```

3. This creates a set of draft documents -- one for every task in your BPMN diagram
4. Open the generated files in VS Code and fill in the content sections with your
   business knowledge

**What does `--skip-llm` mean?** "LLM" stands for Large Language Model -- an AI
system like ChatGPT or Claude. Adding `--skip-llm` tells the tool to create blank
templates for you to fill in manually, rather than asking an AI to generate content.
Use this option if you do not have an AI API key set up, or if you prefer to write
everything yourself.

### If You Want AI to Help Fill In Content

If your organization has an API key for an AI service, you can let the tool generate
initial drafts of the content. You will still need to review and correct everything
the AI writes.

First, set up your API key. In the terminal:

- **Windows:**
  ```
  set ANTHROPIC_API_KEY=your-key-here
  ```
- **Mac or Linux:**
  ```
  export ANTHROPIC_API_KEY=your-key-here
  ```

Replace `your-key-here` with the actual key from your administrator.

Then run the ingest command without `--skip-llm`:

```
python ../../cli/mda.py ingest bpmn/your-file.bpmn
```

The AI will generate draft content for each task. **Always review AI-generated
content carefully.** The AI does not know your specific business rules -- you do.

---

## Working with the Knowledge Corpus

### What Is the Corpus?

The **corpus** is your organization's knowledge library. It contains all the
reference materials that your process documents draw from. Think of it as the
filing cabinet that holds your procedures manual, your policy handbook, and your
regulatory references.

The corpus is organized into categories:

| Category | What It Contains | Example |
|----------|-----------------|---------|
| **Procedures** | Step-by-step work instructions | "How to verify W-2 income" |
| **Policies** | Organizational rules and guidelines | "Income documentation retention policy" |
| **Regulations** | External compliance requirements | "Fannie Mae Selling Guide B3-3.1-01" |
| **Rules** | Decision tables and thresholds | "DTI ratio limits by loan type" |
| **Data Definitions** | What each data field means | "Definition of qualifying income" |
| **System Docs** | How backend systems work | "DocVault API reference" |
| **Training** | Onboarding and training materials | "New underwriter orientation guide" |
| **Glossary** | Term definitions | "What does DTI mean?" |

### Finding Existing Documents

To search the corpus for documents related to a topic:

```
python ../../cli/mda.py corpus search "income"
```

This returns a list of all corpus documents that mention "income." You can also
filter by type or domain:

```
python ../../cli/mda.py corpus search "income" --type procedure
python ../../cli/mda.py corpus search "income" --domain "Mortgage Lending"
```

### Adding a New Document

To create a new corpus document from a template:

```
python ../../cli/mda.py corpus add procedure --domain "Mortgage Lending" --title "My New Procedure"
```

This creates a new file with a blank template. Open it in VS Code (it will appear
in the `corpus/procedures/` folder) and fill in the content.

You can replace `procedure` with any of the other types: `policy`, `regulation`,
`rule`, `data-dictionary`, `system`, `training`, or `glossary`.

### Rebuilding the Corpus Index

After adding or changing corpus documents, rebuild the index so the tools can find
them:

```
python ../../cli/mda.py corpus index
```

### If Your Corpus Is Stored in the Cloud (S3)

Your administrator may have configured the corpus to load from Amazon S3, which is
a cloud file storage service. If so, you do not need to do anything special -- the
tools automatically download the latest documents when you run commands.

You can check your configuration by opening the `mda.config.yaml` file in your
process folder. If you see a section like this, your corpus is on S3:

```yaml
corpus:
  source: "s3"
  s3:
    bucket: "my-company-corpus"
    prefix: "corpus/"
    region: "us-east-1"
```

---

## Editing Documents

### Opening a Capsule File

1. In the VS Code left panel, expand the folders: `triples` > `verify-w2`
2. Click on `verify-w2.cap.md` to open it
3. The file appears in the main editing area

You can also open files by pressing **Ctrl+P** in VS Code, then typing part of the
file name (for example, type `verify-w2` and select the `.cap.md` file from the
list).

### What to Edit

Focus your edits on the **content sections** below the front matter (below the
second `---` line):

- **Purpose** -- A clear summary of what this task accomplishes
- **Procedure** -- Numbered steps describing exactly how the work is done
- **Business Rules** -- Bullet points listing the rules that govern decisions
- **Regulatory Context** -- Citations to regulations, guidelines, and compliance
  requirements
- **Inputs** -- What data or documents this task needs to begin
- **Outputs** -- What data or documents this task produces when complete
- **Exceptions** -- What happens when something goes wrong or an edge case occurs

Write in plain English. Use numbered lists for sequential steps. Use bullet points
for rules and requirements. Be specific -- imagine you are writing instructions for
a new employee who has never done this task before.

### What NOT to Edit

Do not change anything in the **front matter** block (between the `---` markers at
the top of the file). Specifically, do not change:

- `capsule_id`, `intent_id`, or `contract_id` -- unique identifiers managed by the
  tools
- `predecessor_ids` and `successor_ids` -- these define the process flow and are
  generated from the BPMN diagram
- `bpmn_task_id` or `process_id` -- these link the document to the BPMN diagram
- `version` -- updated automatically when changes are submitted

If you believe any of these values are wrong, talk to your team lead rather than
changing them yourself.

### Saving Your Work

Press **Ctrl+S** to save the file, just like in Word. Git automatically tracks
your changes in the background. You do not need to do anything extra to "save to
Git" -- that happens when you submit (covered below).

> **Tip:** VS Code shows a white dot on the file tab when you have unsaved changes.
> After you press Ctrl+S, the dot disappears.

---

## Checking Your Work

Before submitting your changes, run the built-in checks to make sure everything
is valid.

### Quick Check (About 30 Seconds)

```
python ../../cli/mda.py test --quick
```

This runs a small set of fast checks to catch obvious problems, like missing
required fields or broken links between tasks.

### Full Check (About 1 Minute)

```
python ../../cli/mda.py test
```

This runs all available checks, including deeper analysis of data flow consistency,
cross-references, and corpus coverage.

### Health Report

```
python ../../cli/mda.py report
```

This produces a detailed health report showing grades for each task and dimension.
To see the output in a more readable format:

```
python ../../cli/mda.py report --format yaml
```

Look at the grades:
- **A or B** -- Your work is in good shape
- **C** -- Acceptable, but there are gaps you could fill
- **D or F** -- Important information is missing; address these before submitting

### View Specific Gaps

To see exactly what knowledge is missing, and focus on the most important items:

```
python ../../cli/mda.py gaps --severity high
```

This shows only high-severity gaps. You can also use `--severity critical` to see
only the most urgent items, or run `python ../../cli/mda.py gaps` with no filter to
see everything.

---

## Submitting Your Changes

When you are satisfied with your edits and the checks pass, it is time to submit
your changes for review.

Make sure you are in the **project root folder** (not inside an example folder).
If you are unsure, type `cd` followed by the path to the project root. Then run:

```
python cli/mda.py submit --message "Updated income verification procedures for gig economy workers"
```

Replace the message in quotes with a brief description of what you changed. Be
specific -- this message helps reviewers understand your changes at a glance.

**What this command does, step by step:**

1. **Creates a branch** -- Think of this as making a copy of the documents so your
   changes do not affect the official versions until they are approved
2. **Commits your edits** -- Saves a snapshot of all your changes with your
   description message attached
3. **Pushes to the shared repository** -- Uploads your changes to the team's shared
   server so others can see them
4. **Creates a pull request** -- Sends a formal request for your team lead to review
   and approve your changes (like sending a document for sign-off)

### What Happens Next

- Your team lead (or designated reviewer) receives a notification that you have
  submitted changes
- They review your edits and may leave comments or request changes
- If they request changes, you will get a notification -- make the requested edits,
  save, and submit again
- Once approved, your changes are merged into the official documents and go live

---

## Browsing Your Process as a Website

You can view your entire process as a nicely formatted website in your browser.
In the terminal, navigate to your process folder and run:

```
python ../../cli/mda.py docs serve
```

Then open your web browser and go to **http://localhost:8000**. You will see:

- A visual process flow diagram
- All tasks with their capsule documents
- Knowledge corpus documents
- Gaps and health scores

Press **Ctrl+C** in the terminal to stop the website when you are done.

---

## Daily Workflow Cheat Sheet

Here are the commands you will use most often. Keep this page bookmarked or printed
for quick reference.

**Before using these commands,** make sure your terminal is in the right folder.
Most commands should be run from inside your process folder (e.g.,
`examples/income-verification/`).

| What You Want to Do | Command |
|---------------------|---------|
| See all tasks in my process | `python ../../cli/mda.py status` |
| Quick-check my work | `python ../../cli/mda.py test --quick` |
| Full check | `python ../../cli/mda.py test` |
| See health scores | `python ../../cli/mda.py report --format yaml` |
| Find a corpus document | `python ../../cli/mda.py corpus search "keyword"` |
| Add a new procedure | `python ../../cli/mda.py corpus add procedure --title "My Procedure"` |
| View missing information | `python ../../cli/mda.py gaps` |
| View only critical gaps | `python ../../cli/mda.py gaps --severity critical` |
| See the process flow | `python ../../cli/mda.py graph --format mermaid` |
| Browse as a website | `python ../../cli/mda.py docs serve` |
| Rebuild corpus index | `python ../../cli/mda.py corpus index` |
| Submit for review | `python cli/mda.py submit -m "My changes"` (from project root) |

> **Note on the submit command:** The submit command should be run from the
> **project root folder**, not from inside a process folder. That is why it uses
> `cli/mda.py` instead of `../../cli/mda.py`.

---

## A Typical Day

Here is what a normal workday might look like:

1. **Open VS Code** and open the project folder
2. **Open the terminal** (Ctrl+\`) and navigate to your process folder
3. **Check status** to see what tasks need attention:
   ```
   python ../../cli/mda.py status
   ```
4. **Open a capsule file** from the left panel and read through it
5. **Edit the content** -- add procedure steps, business rules, or regulatory
   references based on your expertise
6. **Save** your changes (Ctrl+S)
7. **Run a quick check** to make sure you did not break anything:
   ```
   python ../../cli/mda.py test --quick
   ```
8. **Check your health scores** to see if your edits improved things:
   ```
   python ../../cli/mda.py report --format yaml
   ```
9. **Repeat** steps 4-8 for other tasks
10. **When you are done for the day**, submit your changes:
    ```
    cd ../..
    python cli/mda.py submit -m "Added DTI calculation rules and W-2 verification steps"
    ```

---

## If You Are Using an AI Assistant

If you have an AI coding assistant installed in VS Code (such as Claude Code,
GitHub Copilot, or Cursor), you can ask it to run commands for you using natural
language. For example:

- "Show me the status of my triples"
- "Search the corpus for income verification"
- "Run the health report"
- "What gaps are there in my process?"
- "Submit my changes with the message 'updated DTI procedures'"

The AI assistant will figure out which `mda` command to run and execute it for you.
This can save you from memorizing command syntax.

### Claude Code Slash Commands

If you are using Claude Code specifically, the project includes custom slash
commands that map directly to MDA operations:

- `/mda-status` -- Show the status of your process
- `/mda-test` -- Run verification checks
- `/mda-submit` -- Submit your changes for review

Type these in the Claude Code chat panel to run them instantly.

### Important Note About AI Assistants

An AI assistant is a convenience, not a requirement. Every single task in this
guide can be done by typing the commands yourself in the terminal. If the AI
assistant gives you unexpected results, try typing the command manually using
the cheat sheet above.

---

## Troubleshooting

### "python is not recognized as an internal or external command"

Python is not installed, or it was installed without being added to your system
PATH.

**Fix:** Uninstall Python, then reinstall it. On the very first screen of the
installer, check the box that says **"Add Python to PATH"** before clicking
"Install Now." After reinstalling, close and reopen VS Code.

### "No module named 'yaml'" or "ModuleNotFoundError"

The project dependencies are not installed.

**Fix:** In the terminal, navigate to the project root folder and run:

```
pip install -r requirements.txt
```

If that does not work, try:

```
pip3 install -r requirements.txt
```

### "No changes to submit"

You either have not saved any changes to your files, or you already submitted
your current changes.

**Fix:** Make sure you have saved your files (Ctrl+S) and that you have actually
changed something since your last submit.

### "Push failed" or "remote: Repository not found"

Your Git connection to the shared repository is not set up correctly.

**Fix:** Ask your team lead or system administrator for the correct repository
URL and access credentials. They may need to add you to the repository.

### "Corpus directory not found"

The corpus path in your configuration file does not point to a valid location.

**Fix:** Open `mda.config.yaml` in your process folder and check the `paths`
section. Make sure the `corpus` path points to a folder that exists. If you are
unsure, ask your team lead.

### "fatal: not a git repository"

You are running a command from a folder that is not part of the project.

**Fix:** Make sure you are inside the project folder. In the terminal, use `cd`
to navigate to the project root or your process folder.

### A command takes a very long time or seems frozen

The command may be trying to call an AI service (LLM) over the internet.

**Fix:** Press **Ctrl+C** to cancel the command. Then re-run it with the
`--skip-llm` flag to skip AI calls. For example:

```
python ../../cli/mda.py ingest bpmn/my-file.bpmn --skip-llm
```

### "Permission denied" errors

You may not have write access to certain files or folders.

**Fix:** Ask your IT department or system administrator to grant you write
permissions to the project folder.

### VS Code does not show my files

You may have opened the wrong folder, or not opened a folder at all.

**Fix:** Go to **File > Open Folder** in VS Code and select the `ISLayer`
project folder (or whatever your team has named it).

---

## Glossary of Terms

Here are common terms you will encounter, explained in plain language:

| Term | What It Means |
|------|--------------|
| **BPMN** | Business Process Model and Notation -- a standard way to draw flowcharts of business processes |
| **Capsule** | A document describing a single task in your process, including its purpose, procedure, rules, and data |
| **CLI** | Command Line Interface -- the terminal where you type commands |
| **Commit** | A saved snapshot of your changes, like a checkpoint in a video game |
| **Corpus** | Your organization's knowledge library of procedures, policies, and regulations |
| **Front matter** | The metadata block at the top of a document, between the `---` markers |
| **Gap** | A piece of missing information that needs to be filled in |
| **Git** | A tool that tracks changes to files and lets you share them with your team |
| **Intent** | A structured description of what an AI agent should do to complete a task |
| **LLM** | Large Language Model -- an AI system that can read and generate text |
| **Markdown** | A simple text format that uses symbols like `#` and `-` for formatting |
| **MDA** | Model-Driven Architecture -- the methodology this tool follows |
| **Pull request** | A formal request for someone to review and approve your changes |
| **Repository** | The shared project folder that contains all the files and their history |
| **Terminal** | The text-based command panel at the bottom of VS Code (opened with Ctrl+\`) |
| **Triple** | A set of three linked documents (capsule, intent, contract) that fully describe a task |

---

## Getting Help

If you are stuck, here are your options:

1. **Check this guide** -- the troubleshooting section above covers the most common
   problems
2. **Read the CLI reference** -- the file `docs/cli-reference.md` has detailed
   documentation for every command
3. **Read the process owner guide** -- the file `docs/process-owner-guide.md` has
   more detail about your role in the workflow
4. **Ask your team lead** -- they can help with process-specific questions and
   access issues
5. **Ask your system administrator** -- they can help with installation problems
   and configuration
6. **Ask your AI assistant** -- if you have one set up in VS Code, try describing
   your problem in plain English

---

*Last updated: April 2026*
