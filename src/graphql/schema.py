from ariadne import gql

type_defs = gql("""
    type Query {
        users(first: Int, after: String, last: Int, before: String): UserConnection!
        user(id: ID!): User
        organizations(first: Int, after: String, last: Int, before: String): OrganizationConnection!
        organization(id: ID!): Organization
        studies(first: Int, after: String, last: Int, before: String): StudyConnection!
        study(id: ID!): Study
        reports(first: Int, after: String, last: Int, before: String): ReportConnection!
        report(id: ID!): Report
    }

    type Mutation {
        createUser(input: CreateUserInput!): User!
        updateUser(id: ID!, input: UpdateUserInput!): User!
        deleteUser(id: ID!): Boolean!
        createOrganization(input: CreateOrganizationInput!): Organization!
        updateOrganization(id: ID!, input: UpdateOrganizationInput!): Organization!
        deleteOrganization(id: ID!): Boolean!
        createStudy(input: CreateStudyInput!): Study!
        updateStudy(id: ID!, input: UpdateStudyInput!): Study!
        deleteStudy(id: ID!): Boolean!
        createReport(input: CreateReportInput!): Report!
        updateReport(id: ID!, input: UpdateReportInput!): Report!
        deleteReport(id: ID!): Boolean!
    }

    type User {
        id: ID!
        firstName: String
        lastName: String
        email: String
        phoneNumber: String
        role: String
        createdAt: String!
        organization: Organization
        reports: [Report!]!
    }

    type Organization {
        id: ID!
        name: String!
        logo: String
        address: String
        phoneNumber: String
        users: [User!]!
    }

    type Study {
        id: ID!
        name: String!
        createdAt: String!
        templates: [StudyTemplate!]!
        reports: [Report!]!
    }

    type StudyTemplate {
        id: ID!
        sectionNames: [String!]!
        createdAt: String!
        study: Study!
    }

    type Report {
        id: ID!
        promptText: String
        resultText: String
        status: ReportStatus!
        createdAt: String!
        updatedAt: String
        study: Study!
        template: StudyTemplate
        user: User!
        history: [ReportHistory!]!
        events: [ReportEvent!]!
    }

    type ReportHistory {
        id: ID!
        timestamp: String!
        status: ReportStatus!
        resultText: String
        report: Report!
    }

    type ReportEvent {
        id: ID!
        eventType: String!
        timestamp: String!
        details: String
        report: Report!
    }

    enum ReportStatus {
        DRAFT
        PRELIMINARY
        SIGNED
        SIGNED_WITH_ADDENDUM
    }

    input CreateUserInput {
        firstName: String!
        lastName: String!
        email: String!
        phoneNumber: String
        password: String!
        role: String
        organizationId: ID
    }

    input UpdateUserInput {
        firstName: String
        lastName: String
        email: String
        phoneNumber: String
        role: String
        organizationId: ID
    }

    input CreateOrganizationInput {
        name: String!
        logo: String
        address: String!
        phoneNumber: String!
    }

    input UpdateOrganizationInput {
        name: String
        logo: String
        address: String
        phoneNumber: String
    }

    input CreateStudyInput {
        name: String!
    }

    input UpdateStudyInput {
        name: String
    }

    input CreateReportInput {
        studyId: ID!
        templateId: ID!
        userId: ID!
        promptText: String!
    }

    input UpdateReportInput {
        promptText: String
        resultText: String
        status: ReportStatus
    }

    type PageInfo {
        hasNextPage: Boolean!
        hasPreviousPage: Boolean!
        startCursor: String
        endCursor: String
    }

    type UserEdge {
        cursor: String!
        node: User!
    }

    type UserConnection {
        edges: [UserEdge!]!
        pageInfo: PageInfo!
        totalCount: Int!
    }

    type OrganizationEdge {
        cursor: String!
        node: Organization!
    }

    type OrganizationConnection {
        edges: [OrganizationEdge!]!
        pageInfo: PageInfo!
        totalCount: Int!
    }

    type StudyEdge {
        cursor: String!
        node: Study!
    }

    type StudyConnection {
        edges: [StudyEdge!]!
        pageInfo: PageInfo!
        totalCount: Int!
    }

    type ReportEdge {
        cursor: String!
        node: Report!
    }

    type ReportConnection {
        edges: [ReportEdge!]!
        pageInfo: PageInfo!
        totalCount: Int!
    }

    type StudyTemplateEdge {
        cursor: String!
        node: StudyTemplate!
    }

    type StudyTemplateConnection {
        edges: [StudyTemplateEdge!]!
        pageInfo: PageInfo!
        totalCount: Int!
    }

    type ReportHistoryEdge {
        cursor: String!
        node: ReportHistory!
    }

    type ReportHistoryConnection {
        edges: [ReportHistoryEdge!]!
        pageInfo: PageInfo!
        totalCount: Int!
    }

    type ReportEventEdge {
        cursor: String!
        node: ReportEvent!
    }

    type ReportEventConnection {
        edges: [ReportEventEdge!]!
        pageInfo: PageInfo!
        totalCount: Int!
    }
""")
